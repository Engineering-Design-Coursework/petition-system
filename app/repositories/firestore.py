"""Gerçek veritabanı: Google Firestore.

GÖREV T2.6 — Bu sınıfın birim testi yok (gerçek Firebase gerektirir). Bunun yerine
tests/unit/test_memory_repository.py'deki davranışların aynısını sağlamalı; Faz 3'te
Firestore Emulator ile entegrasyon testi eklenecek.

Veri düzeni:
  petitions/{petition_id}                    -> title, description, goal, owner_uid,
                                                created_at, status, signature_count,
                                                search_text (normalize_text(title + " " + description))
  signatures/{petition_id}_{uid}             -> petition_id, uid, signed_at

Mükerrer imza engeli (önemli!): imza belgesinin id'si "{petition_id}_{uid}" olduğu için
aynı kişi ikinci kez imzalayamaz. Bunu bir transaction içinde yap:

    from google.cloud import firestore

    @firestore.transactional
    def _sign(transaction, petition_ref, signature_ref, data):
        petition_snap = petition_ref.get(transaction=transaction)
        if not petition_snap.exists:
            raise PetitionNotFoundError(...)
        if signature_ref.get(transaction=transaction).exists:
            raise AlreadySignedError(...)
        transaction.create(signature_ref, data)
        new_count = petition_snap.get("signature_count") + 1
        transaction.update(petition_ref, {"signature_count": new_count})
        return new_count

Arama: Firestore "içinde geçiyor" araması yapamaz. Küçük proje için en yeni ~200 kampanyayı
çekip Python'da `matches_query` ile filtrelemek yeterlidir.
"""

from app.domain.models import Petition, Signature


class FirestorePetitionRepository:
    def __init__(self, client) -> None:
        """`client`: firebase_admin.firestore.client() sonucu."""
        self._db = client

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
