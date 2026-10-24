"""Firebase ID token -> User dönüşümü.

Tarayıcı Firebase ile giriş yapar ve bir "ID token" alır. Sunucu bu token'ın gerçekten
Firebase tarafından verildiğini doğrulamalıdır; aksi halde herkes sahte kullanıcı olabilir.
"""

from collections.abc import Callable
from typing import Protocol

from app.domain.models import User


class InvalidTokenError(Exception):
    """Token geçersiz, süresi dolmuş ya da sahte."""


class TokenVerifier(Protocol):
    def verify(self, id_token: str) -> User: ...


class StubTokenVerifier:
    """Testler ve demo modu için: token -> User eşlemesi önceden verilir."""

    def __init__(self, users: dict[str, User]):
        self._users = users

    def verify(self, id_token: str) -> User:
        try:
            return self._users[id_token]
        except KeyError:
            raise InvalidTokenError(id_token) from None


class FirebaseTokenVerifier:
    """GÖREV T2.4 — tests/unit/test_firebase_verifier.py

    `verify_fn` varsayılan olarak firebase_admin.auth.verify_id_token'dır; testlerde
    yerine Mock verilir (gerçek Firebase'e bağlanmadan test edebilmek için).
    """

    def __init__(self, verify_fn: Callable[[str], dict] | None = None):
        if verify_fn is None:
            from firebase_admin import auth

            verify_fn = auth.verify_id_token
        self._verify_fn = verify_fn

    def verify(self, id_token: str) -> User:
        """self._verify_fn(id_token) bir sözlük (claims) döner. Bunu User'a çevir:

            uid            <- claims["uid"]
            email          <- claims.get("email")
            email_verified <- claims.get("email_verified", False)
            phone_number   <- claims.get("phone_number")
            display_name   <- claims.get("name")

        token boşsa ya da self._verify_fn herhangi bir hata fırlatırsa InvalidTokenError fırlat.
        """
        # Boş token Firebase'e gitmez
        if not id_token:
            raise InvalidTokenError("Token boş")

        # Firebase'in her hatası geçersiz token sayılır
        try:
            claims = self._verify_fn(id_token)
        except Exception as error:
            raise InvalidTokenError(str(error)) from error

        return User(
            uid=claims["uid"],
            email=claims.get("email"),
            email_verified=claims.get("email_verified", False),
            phone_number=claims.get("phone_number"),
            display_name=claims.get("name"),
        )
