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

from app.routes.deps import render

router = APIRouter()


@router.get("/", name="home")
def home(request: Request):
    # GÖREV T1.7: son 6 kampanyayı da göster:
    #   petitions = petition_service(request).list_recent(limit=6)
    return render(request, "home.html", {"petitions": []})


@router.get("/health", name="health")
def health():
    return {"status": "ok"}


@router.get("/petitions", name="petition_list")
def petition_list(request: Request):
    """GÖREV T1.7 — son 50 kampanyayı "petitions/list.html" ile göster.
    Şablon değişkeni: petitions (list[Petition])"""
    raise NotImplementedError


@router.get("/petitions/new", name="petition_new")
def petition_new(request: Request):
    """GÖREV T1.7 — kampanya oluşturma formu.
    Giriş yapılmamışsa: return login_redirect("/petitions/new")
    Aksi halde "petitions/new.html" çiz; değişkenler: errors={}, form={}"""
    raise NotImplementedError


@router.post("/petitions", name="petition_create")
def petition_create(
    request: Request,
    title: str = Form(""),
    description: str = Form(""),
    goal: str = Form(""),
):
    """GÖREV T1.7 — formdan gelen kampanyayı kaydet.
    - Giriş yoksa: login_redirect("/petitions/new")
    - goal tam sayıya çevrilemiyorsa: errors={"goal": "Hedef bir sayı olmalı."}, 400
    - petition_service(request).create(...) ValidationError fırlatırsa:
        "petitions/new.html" errors=e.errors, form={girilen değerler}, status_code=400
    - Başarılıysa: RedirectResponse(f"/petitions/{petition.id}", status_code=303)"""
    raise NotImplementedError


@router.get("/petitions/{petition_id}", name="petition_detail")
def petition_detail(request: Request, petition_id: str, signed: int = 0):
    """GÖREV T1.7 (+ T2.5'te paylaşım linkleri)
    "petitions/detail.html" değişkenleri:
      petition     -> petition_service(request).get(petition_id)
      percent      -> progress_percent(petition.signature_count, petition.goal)
      share_url    -> request.app.state.settings.base_url + "/petitions/" + petition.id
      share_links  -> T1.7'de {} ; T2.5'te build_share_links(share_url, petition.title)
      message      -> signed == 1 ise "İmzanız alındı, teşekkürler!", değilse None"""
    raise NotImplementedError


@router.get("/petitions/{petition_id}/progress", name="petition_progress")
def petition_progress(request: Request, petition_id: str):
    """GÖREV T2.5 — htmx her 5 saniyede bu adresi çağırır ve ilerleme çubuğunu yeniler.
    "partials/progress.html" değişkenleri: petition, percent"""
    raise NotImplementedError


@router.post("/petitions/{petition_id}/sign", name="petition_sign")
def petition_sign(request: Request, petition_id: str):
    """GÖREV T2.5 — imza at.
    - Giriş yoksa: login_redirect(f"/petitions/{petition_id}")
    - signature_service(request).sign(user, petition_id)
    - Başarılıysa: RedirectResponse(f"/petitions/{petition_id}?signed=1", status_code=303)
    - NotEligibleError olursa detay sayfasını message ile tekrar çiz:
        NOT_VERIFIED    -> 403, "İmza atmak için e-postanızı ya da telefonunuzu doğrulayın."
        ALREADY_SIGNED  -> 409, "Bu kampanyayı zaten imzaladınız."
        PETITION_CLOSED -> 409, "Bu kampanya imzaya kapalı."
    (Kampanya yoksa PetitionNotFoundError -> otomatik 404.)"""
    raise NotImplementedError


@router.get("/search", name="search")
def search(request: Request, q: str = ""):
    """GÖREV T1.7 — "search.html" değişkenleri: query=q, results=petition_service(request).search(q)"""
    raise NotImplementedError
