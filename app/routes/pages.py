"""Kampanya sayfaları.

`home` ve `health` örnek olarak hazır yazıldı; diğerleri GÖREV olarak bekliyor.
Testler: tests/integration/test_petition_pages.py (T1.7), tests/integration/test_signing.py (T2.5)

Kullanışlı yardımcılar (app/routes/deps.py):
  render(request, "şablon.html", {...}, status_code=200)  -> sayfa çizer
  current_user(request)                                   -> User ya da None
  login_redirect("/geri/donulecek/adres")                 -> giriş sayfasına yönlendirir
  petition_service(request), signature_service(request)   -> servisler
PetitionNotFoundError fırlatılırsa uygulama otomatik 404 sayfası döner (app/main.py).
"""

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.domain.errors import ValidationError
from app.domain.progress import progress_percent
from app.routes.deps import (
    current_user,
    login_redirect,
    petition_service,
    render,
)

router = APIRouter()


@router.get("/", name="home")
def home(request: Request):
    petitions = petition_service(request).list_recent(limit=6)
    return render(request, "home.html", {"petitions": petitions})


@router.get("/health", name="health")
def health():
    return {"status": "ok"}


@router.get("/petitions", name="petition_list")
def petition_list(request: Request):
    petitions = petition_service(request).list_recent(limit=50)
    return render(request, "petitions/list.html", {"petitions": petitions})


@router.get("/petitions/new", name="petition_new")
def petition_new(request: Request):
    if current_user(request) is None:
        return login_redirect("/petitions/new")

    return render(
        request,
        "petitions/new.html",
        {"errors": {}, "form": {}},
    )


@router.post("/petitions", name="petition_create")
def petition_create(
    request: Request,
    title: str = Form(""),
    description: str = Form(""),
    goal: str = Form(""),
):
    user = current_user(request)
    if user is None:
        return login_redirect("/petitions/new")

    form = {
        "title": title,
        "description": description,
        "goal": goal,
    }

    try:
        goal_value = int(goal)
    except (TypeError, ValueError):
        return render(
            request,
            "petitions/new.html",
            {
                "errors": {"goal": "Hedef bir sayı olmalı."},
                "form": form,
            },
            status_code=400,
        )

    try:
        petition = petition_service(request).create(
            user,
            title,
            description,
            goal_value,
        )
    except ValidationError as exc:
        return render(
            request,
            "petitions/new.html",
            {"errors": exc.errors, "form": form},
            status_code=400,
        )

    return RedirectResponse(
        url=f"/petitions/{petition.id}",
        status_code=303,
    )


@router.get("/petitions/{petition_id}", name="petition_detail")
def petition_detail(
    request: Request,
    petition_id: str,
    signed: int = 0,
):
    petition = petition_service(request).get(petition_id)
    percent = progress_percent(
        petition.signature_count,
        petition.goal,
    )

    base_url = request.app.state.settings.base_url.rstrip("/")
    share_url = f"{base_url}/petitions/{petition.id}"
    message = "İmzanız alındı, teşekkürler!" if signed == 1 else None

    return render(
        request,
        "petitions/detail.html",
        {
            "petition": petition,
            "percent": percent,
            "share_url": share_url,
            "share_links": {},
            "message": message,
        },
    )


@router.get("/petitions/{petition_id}/progress", name="petition_progress")
def petition_progress(request: Request, petition_id: str):
    """GÖREV T2.5 — canlı ilerleme uç noktası."""
    raise NotImplementedError


@router.post("/petitions/{petition_id}/sign", name="petition_sign")
def petition_sign(request: Request, petition_id: str):
    """GÖREV T2.5 — kampanyaya imza atma uç noktası."""
    raise NotImplementedError


@router.get("/search", name="search")
def search(request: Request, q: str = ""):
    results = petition_service(request).search(q)
    return render(
        request,
        "search.html",
        {"query": q, "results": results},
    )
