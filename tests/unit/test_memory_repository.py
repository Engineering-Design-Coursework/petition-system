"""T1.5 — Bellek içi veritabanı (InMemoryPetitionRepository). Döngü kapsamı: 0, 1, çok kayıt."""

from datetime import timedelta

import pytest

from app.domain.errors import AlreadySignedError, PetitionNotFoundError
from app.domain.models import Signature
from app.repositories.memory import InMemoryPetitionRepository
from tests.helpers import FIXED_NOW, make_petition

# GÖREV T1.5 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T1.5 henüz yapılmadı")


@pytest.fixture
def repo():
    return InMemoryPetitionRepository()


def _signature(petition_id="1", uid="u1"):
    return Signature(petition_id=petition_id, uid=uid, signed_at=FIXED_NOW)


# --- add_petition / get_petition -------------------------------------------------


def test_should_assign_sequential_ids_when_id_is_empty(repo):
    first = repo.add_petition(make_petition())
    second = repo.add_petition(make_petition())

    assert (first.id, second.id) == ("1", "2")


def test_should_keep_given_id_when_id_is_not_empty(repo):
    saved = repo.add_petition(make_petition(id="ozel-id"))

    assert saved.id == "ozel-id"
    assert repo.get_petition("ozel-id") == saved


def test_should_return_saved_petition_when_getting_by_id(repo):
    saved = repo.add_petition(make_petition(title="Yemekhane fiyatları düşürülsün"))

    assert repo.get_petition(saved.id) == saved


def test_should_return_none_when_petition_does_not_exist(repo):
    assert repo.get_petition("yok") is None


def test_should_return_a_copy_so_outside_changes_do_not_leak(repo):
    saved = repo.add_petition(make_petition())

    saved.title = "Dışarıda değiştirildi"

    assert repo.get_petition(saved.id).title != "Dışarıda değiştirildi"


# --- list_recent -----------------------------------------------------------------


def test_should_return_empty_list_when_repository_is_empty(repo):
    assert repo.list_recent() == []


def test_should_return_single_petition_when_only_one_exists(repo):
    saved = repo.add_petition(make_petition())

    assert repo.list_recent() == [saved]


def test_should_list_newest_first_and_respect_limit(repo):
    old = repo.add_petition(make_petition(title="Eski kampanya başlığı", created_at=FIXED_NOW))
    new = repo.add_petition(
        make_petition(title="Yeni kampanya başlığı", created_at=FIXED_NOW + timedelta(days=1))
    )
    mid = repo.add_petition(
        make_petition(title="Orta kampanya başlığı", created_at=FIXED_NOW + timedelta(hours=1))
    )

    assert [p.id for p in repo.list_recent()] == [new.id, mid.id, old.id]
    assert [p.id for p in repo.list_recent(limit=2)] == [new.id, mid.id]


# --- search ----------------------------------------------------------------------


def test_should_find_petitions_by_title_or_description(repo):
    by_title = repo.add_petition(make_petition(title="Kampüse bisiklet yolu yapılsın"))
    by_description = repo.add_petition(
        make_petition(
            title="Ulaşım talebimiz var",
            description="Kampüs içinde bisiklet park alanı olmadığı için " + "x" * 20,
            created_at=FIXED_NOW + timedelta(minutes=1),
        )
    )
    repo.add_petition(make_petition(title="Kütüphane 7/24 açık olsun", description="y" * 60))

    results = repo.search("bisiklet")

    assert [p.id for p in results] == [by_description.id, by_title.id]


def test_should_respect_limit_when_searching(repo):
    for minute in range(3):
        repo.add_petition(make_petition(created_at=FIXED_NOW + timedelta(minutes=minute)))

    assert len(repo.search("bisiklet", limit=2)) == 2


def test_should_return_empty_list_when_nothing_matches(repo):
    repo.add_petition(make_petition())

    assert repo.search("otopark") == []


# --- add_signature / has_signed --------------------------------------------------


def test_should_increase_count_and_return_new_count_when_signing(repo):
    petition = repo.add_petition(make_petition())

    first = repo.add_signature(_signature(petition.id, "u1"))
    second = repo.add_signature(_signature(petition.id, "u2"))

    assert (first, second) == (1, 2)
    assert repo.get_petition(petition.id).signature_count == 2


def test_should_reject_duplicate_signature_and_keep_count(repo):
    petition = repo.add_petition(make_petition())
    repo.add_signature(_signature(petition.id, "u1"))

    with pytest.raises(AlreadySignedError):
        repo.add_signature(_signature(petition.id, "u1"))

    assert repo.get_petition(petition.id).signature_count == 1


def test_should_raise_not_found_when_signing_unknown_petition(repo):
    with pytest.raises(PetitionNotFoundError):
        repo.add_signature(_signature("yok", "u1"))


def test_should_track_signatures_per_petition(repo):
    a = repo.add_petition(make_petition())
    b = repo.add_petition(make_petition())

    repo.add_signature(_signature(a.id, "u1"))

    assert repo.has_signed(a.id, "u1") is True
    assert repo.has_signed(b.id, "u1") is False
    assert repo.has_signed(a.id, "u2") is False


def test_should_allow_same_user_to_sign_different_petitions(repo):
    a = repo.add_petition(make_petition())
    b = repo.add_petition(make_petition())

    repo.add_signature(_signature(a.id, "u1"))

    assert repo.add_signature(_signature(b.id, "u1")) == 1
