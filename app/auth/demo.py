"""Firebase ayarlanmamışken (demo modu) giriş için hazır kullanıcılar.

Giriş sayfasında bu token'lar için birer buton çıkar. Gerçek ortamda (APP_ENV=prod) kullanılmaz.
"""

from app.domain.models import User

DEMO_USERS: dict[str, User] = {
    "demo-email": User(
        uid="demo-ayse",
        email="ayse@example.com",
        email_verified=True,
        display_name="Ayşe (e-postası doğrulanmış)",
    ),
    "demo-phone": User(
        uid="demo-mehmet",
        phone_number="+905550000000",
        display_name="Mehmet (telefonu doğrulanmış)",
    ),
    "demo-unverified": User(
        uid="demo-can",
        email="can@example.com",
        email_verified=False,
        display_name="Can (doğrulanmamış)",
    ),
}
