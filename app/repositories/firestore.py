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

from dataclasses import replace

from google.cloud import firestore

from app.domain.errors import AlreadySignedError, PetitionNotFoundError
from app.domain.models import Petition, PetitionStatus, Signature
from app.domain.search import matches_query, normalize_text


def _petition_data(petition: Petition) -> dict:
    """Kampanyayı Firestore'da saklanacak düz sözlüğe dönüştürür."""
    return {
        "title": petition.title,
        "description": petition.description,
        "goal": petition.goal,
        "owner_uid": petition.owner_uid,
        "created_at": petition.created_at,
        "status": petition.status.value,
        "signature_count": petition.signature_count,
        "search_text": normalize_text(f"{petition.title} {petition.description}"),
    }


def _petition_from_snapshot(snapshot) -> Petition:
    """Firestore belge anlık görüntüsünü uygulamanın Petition modeline dönüştürür."""
    data = snapshot.to_dict() or {}
    return Petition(
        id=snapshot.id,
        title=data["title"],
        description=data["description"],
        goal=int(data["goal"]),
        owner_uid=data["owner_uid"],
        created_at=data["created_at"],
        status=PetitionStatus(data.get("status", PetitionStatus.OPEN)),
        signature_count=int(data.get("signature_count", 0)),
    )


@firestore.transactional
def _add_signature_in_transaction(transaction, petition_ref, signature_ref, signature_data) -> int:
    """İmzayı ve sayacı Firestore transaction içinde birlikte günceller."""
    petition_snapshot = petition_ref.get(transaction=transaction)
    if not petition_snapshot.exists:
        raise PetitionNotFoundError(petition_ref.id)

    if signature_ref.get(transaction=transaction).exists:
        raise AlreadySignedError(signature_ref.id)

    petition_data = petition_snapshot.to_dict() or {}
    new_count = int(petition_data.get("signature_count", 0)) + 1
    transaction.create(signature_ref, signature_data)
    transaction.update(petition_ref, {"signature_count": new_count})
    return new_count


class FirestorePetitionRepository:
    def __init__(self, client) -> None:
        """`client`: firebase_admin.firestore.client() sonucu."""
        self._db = client

    def add_petition(self, petition: Petition) -> Petition:
        petitions = self._db.collection("petitions")
        document = petitions.document(petition.id) if petition.id else petitions.document()
        stored = replace(petition, id=document.id)
        document.set(_petition_data(stored))
        return replace(stored)

    def get_petition(self, petition_id: str) -> Petition | None:
        snapshot = self._db.collection("petitions").document(petition_id).get()
        if not snapshot.exists:
            return None
        return _petition_from_snapshot(snapshot)

    def list_recent(self, limit: int = 20) -> list[Petition]:
        query = (
            self._db.collection("petitions")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        return [_petition_from_snapshot(snapshot) for snapshot in query.stream()]

    def search(self, query: str, limit: int = 20) -> list[Petition]:
        petitions = self.list_recent(limit=200)
        matches = [
            petition
            for petition in petitions
            if matches_query(f"{petition.title} {petition.description}", query)
        ]
        return matches[:limit]

    def add_signature(self, signature: Signature) -> int:
        petition_ref = self._db.collection("petitions").document(signature.petition_id)
        signature_ref = self._db.collection("signatures").document(f"{signature.petition_id}_{signature.uid}")
        transaction = self._db.transaction()
        return _add_signature_in_transaction(
            transaction,
            petition_ref,
            signature_ref,
            {
                "petition_id": signature.petition_id,
                "uid": signature.uid,
                "signed_at": signature.signed_at,
            },
        )

    def has_signed(self, petition_id: str, uid: str) -> bool:
        signature_id = f"{petition_id}_{uid}"
        return self._db.collection("signatures").document(signature_id).get().exists
