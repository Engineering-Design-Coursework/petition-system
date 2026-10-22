"""İmza atabilme kuralı — karar tablosu (tests/unit/test_eligibility.py)."""

from dataclasses import dataclass
from enum import StrEnum

from app.domain.models import Petition, PetitionStatus, User


class SignBlockReason(StrEnum):
    NOT_LOGGED_IN = "not_logged_in"
    PETITION_CLOSED = "petition_closed"
    NOT_VERIFIED = "not_verified"
    ALREADY_SIGNED = "already_signed"


@dataclass(frozen=True)
class SignDecision:
    allowed: bool
    reason: SignBlockReason | None = None


def check_can_sign(user: User | None, petition: Petition, already_signed: bool) -> SignDecision:
    if user is None:
        return SignDecision(False, SignBlockReason.NOT_LOGGED_IN)
    elif petition.status == PetitionStatus.CLOSED:
        return SignDecision(False, SignBlockReason.PETITION_CLOSED)
    elif not user.is_verified:
        return SignDecision(False, SignBlockReason.NOT_VERIFIED)
    elif already_signed:
        return SignDecision(False, SignBlockReason.ALREADY_SIGNED)

    return SignDecision(True, None)
