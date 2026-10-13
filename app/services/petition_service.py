"""Kampanya iş mantığı (tests/unit/test_petition_service.py)."""

from app.clock import Clock
from app.domain.models import Petition, User
from app.repositories.base import PetitionRepository


class PetitionService:
    """GÖREV T1.6"""

    def __init__(self, repo: PetitionRepository, clock: Clock):
        self.repo = repo
        self.clock = clock

    def create(self, owner: User, title: str, description: str, goal: int) -> Petition:
        """Yeni kampanya açar ve kaydedilmiş halini (id'si dolu) döner.

        - Önce validate_petition_input ile kontrol et; hata varsa ValidationError(hatalar) fırlat.
        - Başlık ve açıklamanın baştaki/sondaki boşluklarını sil.
        - owner_uid = owner.uid, created_at = self.clock.now(), durum OPEN, imza sayısı 0.
        - Kaydetmek için self.repo.add_petition kullan (id'yi repository verir).
        """
        raise NotImplementedError

    def get(self, petition_id: str) -> Petition:
        """Kampanyayı döner; yoksa PetitionNotFoundError fırlatır."""
        raise NotImplementedError

    def list_recent(self, limit: int = 20) -> list[Petition]:
        """Repository'deki en yeni kampanyalar."""
        raise NotImplementedError

    def search(self, query: str, limit: int = 20) -> list[Petition]:
        """Sorgu boş ya da sadece boşluksa boş liste döner, değilse repo.search sonucunu."""
        raise NotImplementedError
