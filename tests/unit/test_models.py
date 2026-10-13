"""T1.1 — Kullanıcı doğrulanmış mı (User.is_verified). Koşul / MC/DC kapsamı."""

import pytest

from app.domain.models import User

# GÖREV T1.1 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T1.1 henüz yapılmadı")


@pytest.mark.parametrize(
    ("email", "email_verified", "phone", "expected"),
    [
        pytest.param("a@example.com", True, None, True, id="dogrulanmis-eposta"),
        pytest.param("a@example.com", False, None, False, id="dogrulanmamis-eposta"),
        pytest.param(None, False, "+905551112233", True, id="sadece-telefon"),
        pytest.param("a@example.com", False, "+905551112233", True, id="dogrulanmamis-eposta-ama-telefon"),
        pytest.param(None, False, None, False, id="hicbiri-yok"),
        pytest.param(None, True, None, False, id="eposta-yokken-verified-bayragi"),
    ],
)
def test_should_report_verification_when_email_or_phone_is_verified(email, email_verified, phone, expected):
    # Arrange
    user = User(uid="u1", email=email, email_verified=email_verified, phone_number=phone)

    # Act
    result = user.is_verified

    # Assert
    assert result is expected
