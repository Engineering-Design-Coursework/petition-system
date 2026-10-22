"""T2.1 — İmza uygunluğu (check_can_sign). Karar tablosu (decision table) testleri.

| Kural | Giriş | Kampanya | Doğrulanmış | Daha önce imzalamış | Sonuç           |
|-------|-------|----------|-------------|---------------------|-----------------|
| R1    | hayır | -        | -           | -                   | NOT_LOGGED_IN   |
| R2    | evet  | kapalı   | -           | -                   | PETITION_CLOSED |
| R3    | evet  | açık     | hayır       | -                   | NOT_VERIFIED    |
| R4    | evet  | açık     | evet        | evet                | ALREADY_SIGNED  |
| R5    | evet  | açık     | evet        | hayır               | izin var        |

Not: Bu testler User.is_verified'ı (T1.1) kullanır.
"""

import pytest

from app.domain.eligibility import SignBlockReason, SignDecision, check_can_sign
from app.domain.models import PetitionStatus
from tests.helpers import EMAIL_USER, PHONE_USER, UNVERIFIED_USER, make_petition

OPEN = make_petition(id="1")
CLOSED = make_petition(id="2", status=PetitionStatus.CLOSED)
R = SignBlockReason


@pytest.mark.parametrize(
    ("user", "petition", "already_signed", "expected"),
    [
        pytest.param(None, OPEN, False, SignDecision(False, R.NOT_LOGGED_IN), id="R1-giris-yok"),
        pytest.param(None, CLOSED, True, SignDecision(False, R.NOT_LOGGED_IN), id="R1-oncelik"),
        pytest.param(EMAIL_USER, CLOSED, False, SignDecision(False, R.PETITION_CLOSED), id="R2-kapali"),
        pytest.param(UNVERIFIED_USER, CLOSED, False, SignDecision(False, R.PETITION_CLOSED), id="R2-oncelik"),
        pytest.param(
            UNVERIFIED_USER, OPEN, False, SignDecision(False, R.NOT_VERIFIED), id="R3-dogrulanmamis"
        ),
        pytest.param(UNVERIFIED_USER, OPEN, True, SignDecision(False, R.NOT_VERIFIED), id="R3-oncelik"),
        pytest.param(EMAIL_USER, OPEN, True, SignDecision(False, R.ALREADY_SIGNED), id="R4-tekrar"),
        pytest.param(EMAIL_USER, OPEN, False, SignDecision(True, None), id="R5-eposta-ile"),
        pytest.param(PHONE_USER, OPEN, False, SignDecision(True, None), id="R5-telefon-ile"),
    ],
)
def test_should_decide_according_to_decision_table(user, petition, already_signed, expected):
    assert check_can_sign(user, petition, already_signed) == expected
