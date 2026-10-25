"""İmza iş mantığı (tests/unit/test_signature_service.py)."""

from app.clock import Clock
from app.domain.eligibility import SignBlockReason, check_can_sign
from app.domain.errors import AlreadySignedError, NotEligibleError, PetitionNotFoundError
from app.domain.models import Signature, User
from app.repositories.base import PetitionRepository

"""Kullanıcı adına imza atar ve kampanyanın YENİ imza sayısını döner.

        Adımlar:
          1. Kampanyayı repo'dan al; yoksa PetitionNotFoundError.
          2. Kullanıcı varsa daha önce imzalamış mı bak (repo.has_signed).
          3. check_can_sign(...) ile karar ver; izin yoksa NotEligibleError(karar.reason).
          4. repo.add_signature(Signature(petition_id, user.uid, self.clock.now())).
          5. Aynı anda iki istek gelirse repo AlreadySignedError fırlatabilir; bunu
             NotEligibleError(SignBlockReason.ALREADY_SIGNED) olarak yeniden fırlat.
        """


class SignatureService:
    """GÖREV T2.2"""

    def __init__(self, repo: PetitionRepository, clock: Clock):
        self.repo = repo
        self.clock = clock

    def sign(self, user: User | None, petition_id: str) -> int:
        petition = self.repo.get_petition(petition_id)
        if petition is None:
            raise PetitionNotFoundError
        if user:
            has_signed = self.repo.has_signed(petition_id, user.uid)
        else:
            has_signed = False
        decision = check_can_sign(user, petition, has_signed)
        if not (decision.allowed):
            raise NotEligibleError(decision.reason)
        try:
            return self.repo.add_signature(
                Signature(petition_id, user.uid if user else None, self.clock.now())
            )
        except AlreadySignedError:
            raise NotEligibleError(SignBlockReason.ALREADY_SIGNED) from None
