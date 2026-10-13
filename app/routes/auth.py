"""Giriş / çıkış rotaları.

Akış: tarayıcı Firebase ile giriş yapar -> ID token'ı POST /session'a yollar ->
sunucu token'ı doğrular -> kullanıcıyı imzalı oturum çerezine (session cookie) yazar.
Demo modunda giriş sayfasındaki butonlar aynı uç noktaya hazır demo token'larını yollar.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response

from app.auth.demo import DEMO_USERS
from app.auth.verifier import InvalidTokenError
from app.routes.deps import login_user, logout_user, render, safe_next

router = APIRouter()


@router.get("/login", name="login")
def login_page(request: Request, next: str = "/"):
    return render(
        request,
        "login.html",
        {"next": safe_next(next), "demo_users": DEMO_USERS, "error": None},
    )


@router.post("/session", name="session_create")
async def session_create(request: Request):
    is_json = request.headers.get("content-type", "").startswith("application/json")
    data = await request.json() if is_json else await request.form()
    next_path = safe_next(data.get("next"))

    try:
        user = request.app.state.verifier.verify(str(data.get("id_token", "")))
    except InvalidTokenError:
        if is_json:
            return JSONResponse({"detail": "Geçersiz oturum anahtarı."}, status_code=401)
        context = {"next": next_path, "demo_users": DEMO_USERS, "error": "Giriş başarısız."}
        return render(request, "login.html", context, status_code=401)

    login_user(request, user)
    if is_json:
        return Response(status_code=204)
    return RedirectResponse(next_path, status_code=303)


@router.post("/logout", name="logout")
def logout(request: Request):
    logout_user(request)
    return RedirectResponse("/", status_code=303)
