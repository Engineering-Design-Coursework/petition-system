"""İmza iş mantığı (tests/unit/test_signature_service.py)."""

from app.clock import Clock
from app.domain.models import User
from app.repositories.base import PetitionRepository


class SignatureService:
    """GÖREV T2.2"""

    def __init__(self, repo: PetitionRepository, clock: Clock):
        self.repo = repo
        self.clock = clock

    def sign(self, user: User | None, petition_id: str) -> int:
        """Kullanıcı adına imza atar ve kampanyanın YENİ imza sayısını döner.

        Adımlar:
          1. Kampanyayı repo'dan al; yoksa PetitionNotFoundError.
          2. Kullanıcı varsa daha önce imzalamış mı bak (repo.has_signed).
          3. check_can_sign(...) ile karar ver; izin yoksa NotEligibleError(karar.reason).
          4. repo.add_signature(Signature(petition_id, user.uid, self.clock.now())).
          5. Aynı anda iki istek gelirse repo AlreadySignedError fırlatabilir; bunu
             NotEligibleError(SignBlockReason.ALREADY_SIGNED) olarak yeniden fırlat.
        """
        raise NotImplementedError
