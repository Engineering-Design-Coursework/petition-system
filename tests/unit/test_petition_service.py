"""T1.6 — Kampanya servisi (PetitionService). Fake repo + FixedClock; bir testte Mock (spy).

Not: Bu testler InMemoryPetitionRepository'yi (T1.5) ve doğrulamayı (T1.2) kullanır.
"""

from unittest.mock import Mock

import pytest

from app.domain.errors import PetitionNotFoundError, ValidationError
from app.domain.models import PetitionStatus
from app.services.petition_service import PetitionService
from tests.helpers import EMAIL_USER, FIXED_NOW, VALID_DESCRIPTION, VALID_GOAL, VALID_TITLE


@pytest.fixture
def service(repo, clock):
    return PetitionService(repo, clock)


def test_should_create_open_petition_owned_by_user(service, repo):
    # Act
    petition = service.create(EMAIL_USER, VALID_TITLE, VALID_DESCRIPTION, VALID_GOAL)

    # Assert
    assert petition.id
    assert petition.owner_uid == EMAIL_USER.uid
    assert petition.created_at == FIXED_NOW
    assert petition.status is PetitionStatus.OPEN
    assert petition.signature_count == 0
    assert repo.get_petition(petition.id) == petition


def test_should_strip_spaces_from_title_and_description(service):
    petition = service.create(EMAIL_USER, f"  {VALID_TITLE}  ", f"\n{VALID_DESCRIPTION} ", VALID_GOAL)

    assert petition.title == VALID_TITLE
    assert petition.description == VALID_DESCRIPTION


def test_should_raise_validation_error_and_save_nothing_when_input_is_invalid(service, repo):
    with pytest.raises(ValidationError) as excinfo:
        service.create(EMAIL_USER, "kısa", VALID_DESCRIPTION, VALID_GOAL)

    assert "title" in excinfo.value.errors
    assert repo.list_recent() == []


def test_should_return_petition_when_it_exists(service):
    created = service.create(EMAIL_USER, VALID_TITLE, VALID_DESCRIPTION, VALID_GOAL)

    assert service.get(created.id) == created


def test_should_raise_not_found_when_petition_does_not_exist(service):
    with pytest.raises(PetitionNotFoundError):
        service.get("yok")


def test_should_list_recent_petitions(service):
    created = service.create(EMAIL_USER, VALID_TITLE, VALID_DESCRIPTION, VALID_GOAL)

    assert service.list_recent() == [created]


def test_should_find_petitions_when_searching(service):
    created = service.create(EMAIL_USER, VALID_TITLE, VALID_DESCRIPTION, VALID_GOAL)

    assert service.search("kampus") == [created]


@pytest.mark.parametrize("query", ["", "   "])
def test_should_not_query_repository_when_search_is_blank(clock, query):
    # Arrange: Mock bir "spy" gibi kullanılıyor — repo'nun çağrılıp çağrılmadığını kaydeder.
    repo = Mock()
    service = PetitionService(repo, clock)

    # Act
    results = service.search(query)

    # Assert
    assert results == []
    repo.search.assert_not_called()
