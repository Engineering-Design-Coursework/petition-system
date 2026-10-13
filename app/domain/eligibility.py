"""İmza atabilme kuralı — karar tablosu (tests/unit/test_eligibility.py)."""

from dataclasses import dataclass
from enum import StrEnum

from app.domain.models import Petition, User


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
    """GÖREV T2.1

    Kurallar YUKARIDAN AŞAĞIYA kontrol edilir, ilk uyan kural sonucu belirler:
      1. user None ise                        -> SignDecision(False, NOT_LOGGED_IN)
      2. kampanya kapalıysa (CLOSED)          -> SignDecision(False, PETITION_CLOSED)
      3. kullanıcı doğrulanmamışsa            -> SignDecision(False, NOT_VERIFIED)
      4. daha önce imzalamışsa                -> SignDecision(False, ALREADY_SIGNED)
      5. aksi halde                           -> SignDecision(True, None)
    """
    raise NotImplementedError
