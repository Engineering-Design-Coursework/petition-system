"""İmza iş mantığı (tests/unit/test_signature_service.py)."""

from app.clock import Clock
from app.domain.models import User,Signature
from app.repositories.base import PetitionRepository
from app.domain.errors import  NotEligibleError,AlreadySignedError,PetitionNotFoundError
from app.domain.eligibility import check_can_sign ,SignDecision,SignBlockReason
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
       petition=self.repo.get_petition(petition_id)
       if(petition is  None):
            raise PetitionNotFoundError
       if(user):
        Has_signed=self.repo.has_signed(petition_id,user.uid)
       else:Has_signed=False
       decision=check_can_sign(user,petition,Has_signed)
       if not (decision.allowed):
        raise NotEligibleError(decision.reason)
       try:
         return self.repo.add_signature(Signature(petition_id,user.uid if user else False,self.clock.now()))
       except AlreadySignedError: 
        raise NotEligibleError(SignBlockReason.ALREADY_SIGNED)


            

     