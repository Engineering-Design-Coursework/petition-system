"""T2.6 — Firestore veritabanı deposu (FirestorePetitionRepository). Sahte Firestore istemcisi, ağsız."""

from datetime import timedelta

import pytest
from google.cloud import firestore

from app.domain.errors import AlreadySignedError, PetitionNotFoundError
from app.domain.models import PetitionStatus, Signature
from app.repositories.firestore import FirestorePetitionRepository
from tests.helpers import FIXED_NOW, make_petition


class FakeSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


class FakeDocument:
    def __init__(self, store, doc_id):
        self._store = store
        self.id = doc_id

    def get(self, transaction=None):
        return FakeSnapshot(self.id, self._store.get(self.id))

    def set(self, data):
        self._store[self.id] = dict(data)


class FakeQuery:
    def __init__(self, store):
        self._store = store
        self._field = None
        self._descending = False
        self._limit = None

    def order_by(self, field, direction=None):
        self._field = field
        self._descending = direction == firestore.Query.DESCENDING
        return self

    def limit(self, count):
        self._limit = count
        return self

    def stream(self):
        items = list(self._store.items())
        if self._field:
            items.sort(key=lambda item: item[1][self._field], reverse=self._descending)
        if self._limit is not None:
            items = items[: self._limit]
        return [FakeSnapshot(doc_id, data) for doc_id, data in items]


class FakeCollection(FakeQuery):
    def __init__(self, store, counter):
        super().__init__(store)
        self._counter = counter

    def document(self, doc_id=None):
        if doc_id is None:
            self._counter[0] += 1
            doc_id = f"auto-{self._counter[0]}"
        return FakeDocument(self._store, doc_id)


class FakeTransaction:
    """firestore.transactional'ın ihtiyaç duyduğu alanlar + yazmaları commit'e kadar tutar."""

    _read_only = False
    _max_attempts = 1
    _id = b"tx"

    def __init__(self):
        self._writes = []

    def _clean_up(self):
        self._writes = []

    def _begin(self, retry_id=None):
        pass

    def _rollback(self):
        self._writes = []

    def _commit(self):
        for write in self._writes:
            write()
        self._writes = []

    def create(self, ref, data):
        self._writes.append(lambda: ref.set(data))

    def update(self, ref, changes):
        def apply():
            ref._store[ref.id] = {**ref._store[ref.id], **changes}

        self._writes.append(apply)


class FakeFirestoreClient:
    def __init__(self):
        self._stores = {}
        self._counter = [0]

    def collection(self, name):
        store = self._stores.setdefault(name, {})
        return FakeCollection(store, self._counter)

    def transaction(self):
        return FakeTransaction()


@pytest.fixture
def repo():
    return FirestorePetitionRepository(FakeFirestoreClient())


def _signature(petition_id, uid="u1"):
    return Signature(petition_id=petition_id, uid=uid, signed_at=FIXED_NOW)


# --- add_petition / get_petition -------------------------------------------------


def test_should_generate_id_when_id_is_empty(repo):
    saved = repo.add_petition(make_petition())

    assert saved.id != ""
    assert repo.get_petition(saved.id) == saved


def test_should_keep_given_id_when_id_is_not_empty(repo):
    saved = repo.add_petition(make_petition(id="ozel-id"))

    assert saved.id == "ozel-id"


def test_should_keep_all_fields_when_roundtripping(repo):
    original = make_petition(title="Yemekhane", goal=50, status=PetitionStatus.CLOSED)

    saved = repo.add_petition(original)

    loaded = repo.get_petition(saved.id)
    assert loaded.title == "Yemekhane"
    assert loaded.goal == 50
    assert loaded.status is PetitionStatus.CLOSED
    assert loaded.created_at == FIXED_NOW


def test_should_return_none_when_petition_does_not_exist(repo):
    assert repo.get_petition("yok") is None


# --- list_recent -----------------------------------------------------------------


def test_should_return_empty_list_when_no_petitions(repo):
    assert repo.list_recent() == []


def test_should_return_newest_first_when_listing(repo):
    old = repo.add_petition(make_petition(created_at=FIXED_NOW))
    new = repo.add_petition(make_petition(created_at=FIXED_NOW + timedelta(days=1)))

    assert [p.id for p in repo.list_recent()] == [new.id, old.id]


def test_should_respect_limit_when_listing(repo):
    for day in range(3):
        repo.add_petition(make_petition(created_at=FIXED_NOW + timedelta(days=day)))

    assert len(repo.list_recent(limit=2)) == 2


# --- search ----------------------------------------------------------------------


def test_should_find_turkish_text_when_searching_without_diacritics(repo):
    match = repo.add_petition(make_petition(title="Öğrenci yemekhanesi"))
    repo.add_petition(make_petition(title="Bisiklet yolu", description="Güvenli ulaşım için yol."))

    result = repo.search("ogrenci")

    assert [p.id for p in result] == [match.id]


def test_should_return_empty_list_when_nothing_matches(repo):
    repo.add_petition(make_petition())

    assert repo.search("zzzzzz") == []


def test_should_respect_limit_when_searching(repo):
    for day in range(3):
        repo.add_petition(make_petition(title="Yemekhane", created_at=FIXED_NOW + timedelta(days=day)))

    assert len(repo.search("yemekhane", limit=2)) == 2


# --- add_signature / has_signed --------------------------------------------------


def test_should_return_new_count_when_adding_signature(repo):
    saved = repo.add_petition(make_petition(signature_count=4))

    assert repo.add_signature(_signature(saved.id)) == 5
    assert repo.get_petition(saved.id).signature_count == 5


def test_should_mark_as_signed_when_signature_added(repo):
    saved = repo.add_petition(make_petition())

    repo.add_signature(_signature(saved.id, "u1"))

    assert repo.has_signed(saved.id, "u1") is True
    assert repo.has_signed(saved.id, "u2") is False


def test_should_raise_already_signed_and_keep_count_when_signing_twice(repo):
    saved = repo.add_petition(make_petition())
    repo.add_signature(_signature(saved.id))

    with pytest.raises(AlreadySignedError):
        repo.add_signature(_signature(saved.id))

    assert repo.get_petition(saved.id).signature_count == 1


def test_should_raise_not_found_when_signing_missing_petition(repo):
    with pytest.raises(PetitionNotFoundError):
        repo.add_signature(_signature("yok"))
