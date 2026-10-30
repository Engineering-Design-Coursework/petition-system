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

from app.domain.eligibility import SignBlockReason
from app.domain.errors import NotEligibleError, ValidationError
from app.domain.progress import progress_percent
from app.domain.share import build_share_links
from app.routes.deps import (
    current_user,
    login_redirect,
    petition_service,
    render,
    signature_service,
)

router = APIRouter()


def _petition_detail_context(
    request: Request,
    petition,
    message: str | None = None,
    error: str | None = None,
):
    """Kampanya detay sayfasının ortak şablon verisini hazırlar."""
    percent = progress_percent(petition.signature_count, petition.goal)
    base_url = request.app.state.settings.base_url.rstrip("/")
    share_url = f"{base_url}/petitions/{petition.id}"
    return {
        "petition": petition,
        "percent": percent,
        "share_url": share_url,
        "share_links": build_share_links(share_url, petition.title),
        "message": message,
        "error": error,
    }


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
    message = "İmzanız alındı, teşekkürler!" if signed == 1 else None

    return render(
        request,
        "petitions/detail.html",
        _petition_detail_context(request, petition, message=message),
    )


@router.get("/petitions/{petition_id}/progress", name="petition_progress")
def petition_progress(request: Request, petition_id: str):
    """Canlı ilerleme çubuğu için yalnızca güncellenen HTML parçasını döner."""
    petition = petition_service(request).get(petition_id)
    percent = progress_percent(petition.signature_count, petition.goal)
    return render(
        request,
        "partials/progress.html",
        {"petition": petition, "percent": percent},
    )


@router.post("/petitions/{petition_id}/sign", name="petition_sign")
def petition_sign(request: Request, petition_id: str):
    """Geçerli oturumdaki kullanıcı adına kampanyayı imzalar."""
    user = current_user(request)
    if user is None:
        return login_redirect(f"/petitions/{petition_id}")

    try:
        signature_service(request).sign(user, petition_id)
    except NotEligibleError as exc:
        error_responses = {
            SignBlockReason.NOT_VERIFIED: (
                403,
                "İmza atabilmek için e-posta adresinizi veya telefon numaranızı doğrulayın.",
            ),
            SignBlockReason.ALREADY_SIGNED: (409, "Bu kampanyayı zaten imzaladınız."),
            SignBlockReason.PETITION_CLOSED: (409, "Bu kampanya imzaya kapalı."),
        }
        status_code, detail = error_responses[exc.reason]
        petition = petition_service(request).get(petition_id)
        return render(
            request,
            "petitions/detail.html",
            _petition_detail_context(request, petition, error=detail),
            status_code=status_code,
        )

    return RedirectResponse(url=f"/petitions/{petition_id}?signed=1", status_code=303)


@router.get("/search", name="search")
def search(request: Request, q: str = ""):
    results = petition_service(request).search(q)
    return render(
        request,
        "search.html",
        {"query": q, "results": results},
    )
