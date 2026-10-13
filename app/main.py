"""Uygulamanın giriş noktası.

Çalıştırma:  uvicorn app.main:create_app --factory --reload
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.auth.demo import DEMO_USERS
from app.auth.verifier import FirebaseTokenVerifier, StubTokenVerifier, TokenVerifier
from app.clock import Clock, SystemClock
from app.config import Settings, load_settings
from app.domain.errors import PetitionNotFoundError
from app.repositories.base import PetitionRepository
from app.repositories.memory import InMemoryPetitionRepository
from app.routes import auth, pages
from app.routes.deps import render
from app.services.petition_service import PetitionService
from app.services.signature_service import SignatureService

STATIC_DIR = Path(__file__).resolve().parent / "static"


def _firebase_dependencies(settings: Settings) -> tuple[PetitionRepository, TokenVerifier]:
    import firebase_admin
    from firebase_admin import credentials, firestore

    from app.repositories.firestore import FirestorePetitionRepository

    raw = settings.firebase_credentials or ""
    cred_source = json.loads(raw) if raw.lstrip().startswith("{") else raw
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(cred_source))
    return FirestorePetitionRepository(firestore.client()), FirebaseTokenVerifier()


def create_app(
    settings: Settings | None = None,
    repo: PetitionRepository | None = None,
    verifier: TokenVerifier | None = None,
    clock: Clock | None = None,
) -> FastAPI:
    """Uygulamayı kurar. Testler sahte (fake/stub) bağımlılıkları buradan verir."""
    if settings is None:
        load_dotenv()
        settings = load_settings()

    if repo is None or verifier is None:
        if settings.use_firebase:
            default_repo, default_verifier = _firebase_dependencies(settings)
        else:  # demo modu: Firebase yok, veriler bellekte
            default_repo, default_verifier = InMemoryPetitionRepository(), StubTokenVerifier(DEMO_USERS)
        repo = repo or default_repo
        verifier = verifier or default_verifier
    clock = clock or SystemClock()

    app = FastAPI(title="İmza Kampanyası Platformu")
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        https_only=settings.app_env == "prod",
        same_site="lax",
    )
    app.state.settings = settings
    app.state.verifier = verifier
    app.state.petition_service = PetitionService(repo, clock)
    app.state.signature_service = SignatureService(repo, clock)

    @app.exception_handler(PetitionNotFoundError)
    def petition_not_found(request: Request, exc: PetitionNotFoundError):
        return render(request, "404.html", status_code=404)

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.include_router(pages.router)
    app.include_router(auth.router)
    return app
