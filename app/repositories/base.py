"""Veritabanı arayüzü (sözleşme). InMemory ve Firestore sürümleri bu metotları sağlar."""

from typing import Protocol

from app.domain.models import Petition, Signature


class PetitionRepository(Protocol):
    def add_petition(self, petition: Petition) -> Petition:
        """Kaydeder. `petition.id` boşsa yeni benzersiz id atar. Kaydedilmiş hali döner."""
        ...

    def get_petition(self, petition_id: str) -> Petition | None:
        """Kampanyayı döner, yoksa None."""
        ...

    def list_recent(self, limit: int = 20) -> list[Petition]:
        """En yeni kampanyalar önce (created_at azalan), en fazla `limit` tane."""
        ...

    def search(self, query: str, limit: int = 20) -> list[Petition]:
        """Başlığı ya da açıklaması `matches_query` ile eşleşenler, en yeni önce."""
        ...

    def add_signature(self, signature: Signature) -> int:
        """İmzayı kaydeder, kampanyanın imza sayısını 1 artırır ve YENİ sayıyı döner.

        Aynı (petition_id, uid) ikinci kez gelirse AlreadySignedError,
        kampanya yoksa PetitionNotFoundError fırlatır.
        """
        ...

    def has_signed(self, petition_id: str, uid: str) -> bool:
        """Bu kullanıcı bu kampanyayı imzalamış mı?"""
        ...
