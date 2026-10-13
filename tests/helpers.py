"""Testlerde ortak kullanılan sabitler ve küçük yardımcılar."""

from dataclasses import replace
from datetime import UTC, datetime

from app.domain.models import Petition, PetitionStatus, User

FIXED_NOW = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)

VALID_TITLE = "Kampüse bisiklet yolu yapılsın"
VALID_DESCRIPTION = "Kampüs içinde güvenli ulaşım için ayrı bir bisiklet yolu yapılmasını talep ediyoruz."
VALID_GOAL = 100

EMAIL_USER = User(uid="u-email", email="ayse@example.com", email_verified=True)
PHONE_USER = User(uid="u-phone", phone_number="+905551112233")
UNVERIFIED_USER = User(uid="u-unverified", email="can@example.com", email_verified=False)

# StubTokenVerifier için: test token'ı -> kullanıcı
TEST_TOKENS = {
    "token-email": EMAIL_USER,
    "token-phone": PHONE_USER,
    "token-unverified": UNVERIFIED_USER,
}

_BASE_PETITION = Petition(
    id="",
    title=VALID_TITLE,
    description=VALID_DESCRIPTION,
    goal=VALID_GOAL,
    owner_uid="owner-1",
    created_at=FIXED_NOW,
    status=PetitionStatus.OPEN,
    signature_count=0,
)


def make_petition(**overrides) -> Petition:
    """Geçerli bir kampanya üretir; istenen alanlar değiştirilebilir: make_petition(goal=10)."""
    return replace(_BASE_PETITION, **overrides)


def login(client, token: str = "token-email") -> None:
    """Test istemcisini verilen test token'ıyla giriş yapmış hale getirir."""
    response = client.post("/session", data={"id_token": token}, follow_redirects=False)
    assert response.status_code == 303, "Test girişi başarısız"
