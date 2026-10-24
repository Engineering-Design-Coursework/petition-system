"""Bellekte çalışan sahte (Fake) veritabanı.

Testlerde ve Firebase ayarlanmamışken demo modunda kullanılır. Program kapanınca veriler silinir.
"""

from dataclasses import replace

from app.domain.errors import AlreadySignedError, PetitionNotFoundError
from app.domain.models import Petition, Signature
from app.domain.search import matches_query


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
        self._petitions = {}
        self._signatures = set()
        self._next_id = 1

    def add_petition(self, petition: Petition) -> Petition:
        petition = replace(petition)

        # Id yoksa sıradaki numara verilir
        if petition.id == "":
            petition.id = str(self._next_id)
            self._next_id += 1

        self._petitions[petition.id] = petition
        return replace(petition)

    def get_petition(self, petition_id: str) -> Petition | None:
        petition = self._petitions.get(petition_id)
        if petition is None:
            return None
        return replace(petition)

    def list_recent(self, limit: int = 20) -> list[Petition]:
        # En yeni önce
        petitions = sorted(self._petitions.values(), key=lambda p: p.created_at, reverse=True)
        return [replace(p) for p in petitions[:limit]]

    def search(self, query: str, limit: int = 20) -> list[Petition]:
        results = []
        for petition in self.list_recent(limit=len(self._petitions)):
            # Başlık ya da açıklamada ara
            if matches_query(petition.title + " " + petition.description, query):
                results.append(petition)
        return results[:limit]

    def add_signature(self, signature: Signature) -> int:
        petition = self._petitions.get(signature.petition_id)
        if petition is None:
            raise PetitionNotFoundError(signature.petition_id)

        # Aynı kişi ikinci kez imzalayamaz
        key = (signature.petition_id, signature.uid)
        if key in self._signatures:
            raise AlreadySignedError(signature.petition_id)

        self._signatures.add(key)
        petition.signature_count += 1
        return petition.signature_count

    def has_signed(self, petition_id: str, uid: str) -> bool:
        return (petition_id, uid) in self._signatures
