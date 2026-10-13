"""Rotaların ortak yardımcıları. Hazır, değiştirmeye gerek yok."""

from dataclasses import asdict
from pathlib import Path
from urllib.parse import quote

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.domain.models import User
from app.services.petition_service import PetitionService
from app.services.signature_service import SignatureService

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")

SESSION_USER_KEY = "user"


def current_user(request: Request) -> User | None:
    data = request.session.get(SESSION_USER_KEY)
    return User(**data) if data else None


def login_user(request: Request, user: User) -> None:
    request.session[SESSION_USER_KEY] = asdict(user)


def logout_user(request: Request) -> None:
    request.session.pop(SESSION_USER_KEY, None)


def petition_service(request: Request) -> PetitionService:
    return request.app.state.petition_service


def signature_service(request: Request) -> SignatureService:
    return request.app.state.signature_service


def safe_next(path: str | None) -> str:
    """Girişten sonra yalnızca kendi sitemizdeki bir sayfaya dön (open redirect engeli)."""
    if path and path.startswith("/") and not path.startswith("//") and "\\" not in path:
        return path
    return "/"


def login_redirect(next_path: str) -> RedirectResponse:
    return RedirectResponse(f"/login?next={quote(next_path)}", status_code=303)


def render(request: Request, name: str, context: dict | None = None, status_code: int = 200):
    """Şablonu çizer. Her şablonda `user`, `settings` ve `path_for` hazır gelir.

    path_for("petition_detail", petition_id="1") -> "/petitions/1" (rota adından adres üretir)
    """
    ctx = {
        "user": current_user(request),
        "settings": request.app.state.settings,
        "path_for": request.app.url_path_for,
    }
    ctx.update(context or {})
    return templates.TemplateResponse(request, name, ctx, status_code=status_code)
