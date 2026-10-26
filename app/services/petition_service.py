"""Kampanya iş mantığı (tests/unit/test_petition_service.py)."""

from app.clock import Clock
from app.domain.errors import PetitionNotFoundError, ValidationError
from app.domain.models import Petition, User
from app.domain.validation import validate_petition_input
from app.repositories.base import PetitionRepository


class PetitionService:
    """GÖREV T1.6"""

    def __init__(self, repo: PetitionRepository, clock: Clock):
        self.repo = repo
        self.clock = clock

    def create(self, owner: User, title: str, description: str, goal: int) -> Petition:

        if errors := validate_petition_input(title, description, goal):
            raise ValidationError(errors)

        else:
            clean_title = title.strip()
            clean_description = description.strip()
            new = Petition(
                id="",
                title=clean_title,
                description=clean_description,
                goal=goal,
                owner_uid=owner.uid,
                created_at=self.clock.now(),
            )

            return self.repo.add_petition(new)

        """Yeni kampanya açar ve kaydedilmiş halini (id'si dolu) döner.

        - Önce validate_petition_input ile kontrol et; hata varsa ValidationError(hatalar) fırlat.
        - Başlık ve açıklamanın baştaki/sondaki boşluklarını sil.
        - owner_uid = owner.uid, created_at = self.clock.now(), durum OPEN, imza sayısı 0.
        - Kaydetmek için self.repo.add_petition kullan (id'yi repository verir).
        """

    def get(self, petition_id: str) -> Petition:
        """Kampanyayı döner; yoksa PetitionNotFoundError fırlatır."""
        if (petition := self.repo.get_petition(petition_id)) is None:
            raise PetitionNotFoundError
        else:
            return petition

    def list_recent(self, limit: int = 20) -> list[Petition]:
        """Repository'deki en yeni kampanyalar."""

        return self.repo.list_recent(limit=limit)

    def search(self, query: str, limit: int = 20) -> list[Petition]:
        """Sorgu boş ya da sadece boşluksa boş liste döner, değilse repo.search sonucunu."""
        if not query or not query.strip():
            return []
        else:
            return self.repo.search(query=query, limit=limit)
