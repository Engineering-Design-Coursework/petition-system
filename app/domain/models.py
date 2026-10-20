"""Uygulamanın veri yapıları (dataclass).

Bu dosyada iş mantığı yok denecek kadar azdır; tek görev `User.is_verified`.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PetitionStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True)
class User:
    """Firebase ile giriş yapmış kullanıcı."""

    uid: str
    email: str | None = None
    email_verified: bool = False
    phone_number: str | None = None
    display_name: str | None = None

    @property
    def is_verified(self) -> bool:
        if self.email is not None:
            if self.email_verified:
                return True
        if self.phone_number is not None:
            return True
        return False


@dataclass
class Petition:
    """İmza kampanyası. `id` boşsa repository kaydederken yeni id atar."""

    id: str
    title: str
    description: str
    goal: int
    owner_uid: str
    created_at: datetime
    status: PetitionStatus = PetitionStatus.OPEN
    signature_count: int = 0


@dataclass(frozen=True)
class Signature:
    """Bir kullanıcının bir kampanyaya attığı imza."""

    petition_id: str
    uid: str
    signed_at: datetime
