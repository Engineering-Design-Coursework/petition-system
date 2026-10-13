"""Bellekte çalışan sahte (Fake) veritabanı.

Testlerde ve Firebase ayarlanmamışken demo modunda kullanılır. Program kapanınca veriler silinir.
"""

from app.domain.models import Petition, Signature


class InMemoryPetitionRepository:
    """GÖREV T1.5 — tests/unit/test_memory_repository.py

    İpuçları:
      - Kampanyaları bir sözlükte tut: self._petitions[id] = petition
      - İmzaları (petition_id, uid) çiftlerinden oluşan bir sözlükte/kümede tut.
      - Yeni id için sırayla "1", "2", "3"... ver (testler bunu bekler).
      - Dışarıya nesnenin kendisini değil kopyasını ver: dataclasses.replace(petition)
        (yoksa dışarıdaki bir değişiklik veritabanını da değiştirir).
      - Arama için app.domain.search.matches_query kullan.
      - Metot açıklamaları: app/repositories/base.py
    """

    def __init__(self) -> None:
        pass

    def add_petition(self, petition: Petition) -> Petition:
        raise NotImplementedError

    def get_petition(self, petition_id: str) -> Petition | None:
        raise NotImplementedError

    def list_recent(self, limit: int = 20) -> list[Petition]:
        raise NotImplementedError

    def search(self, query: str, limit: int = 20) -> list[Petition]:
        raise NotImplementedError

    def add_signature(self, signature: Signature) -> int:
        raise NotImplementedError

    def has_signed(self, petition_id: str, uid: str) -> bool:
        raise NotImplementedError
