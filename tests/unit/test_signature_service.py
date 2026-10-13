"""T2.2 — İmza servisi (SignatureService). Fake repo + FixedClock; Mock(wraps=...) ile spy.

Not: Bu testler T1.1, T1.5 ve T2.1'i kullanır.
"""

from unittest.mock import Mock

import pytest

from app.domain.eligibility import SignBlockReason
from app.domain.errors import AlreadySignedError, NotEligibleError, PetitionNotFoundError
from app.domain.models import PetitionStatus, Signature
from app.services.signature_service import SignatureService
from tests.helpers import EMAIL_USER, FIXED_NOW, PHONE_USER, UNVERIFIED_USER, make_petition

# GÖREV T2.2 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T2.2 henüz yapılmadı")


@pytest.fixture
def service(repo, clock):
    return SignatureService(repo, clock)


@pytest.fixture
def petition(repo):
    return repo.add_petition(make_petition())


def test_should_record_signature_and_return_new_count(service, repo, petition):
    count = service.sign(EMAIL_USER, petition.id)

    assert count == 1
    assert repo.has_signed(petition.id, EMAIL_USER.uid)


def test_should_count_signatures_from_different_users(service, petition):
    service.sign(EMAIL_USER, petition.id)

    assert service.sign(PHONE_USER, petition.id) == 2


def test_should_reject_second_signature_from_same_user(service, repo, petition):
    service.sign(EMAIL_USER, petition.id)

    with pytest.raises(NotEligibleError) as excinfo:
        service.sign(EMAIL_USER, petition.id)

    assert excinfo.value.reason is SignBlockReason.ALREADY_SIGNED
    assert repo.get_petition(petition.id).signature_count == 1


@pytest.mark.parametrize(
    ("user", "reason"),
    [
        (None, SignBlockReason.NOT_LOGGED_IN),
        (UNVERIFIED_USER, SignBlockReason.NOT_VERIFIED),
    ],
)
def test_should_reject_user_who_is_not_eligible(service, repo, petition, user, reason):
    with pytest.raises(NotEligibleError) as excinfo:
        service.sign(user, petition.id)

    assert excinfo.value.reason is reason
    assert repo.get_petition(petition.id).signature_count == 0


def test_should_reject_signature_when_petition_is_closed(service, repo):
    closed = repo.add_petition(make_petition(status=PetitionStatus.CLOSED))

    with pytest.raises(NotEligibleError) as excinfo:
        service.sign(EMAIL_USER, closed.id)

    assert excinfo.value.reason is SignBlockReason.PETITION_CLOSED


def test_should_raise_not_found_when_petition_does_not_exist(service):
    with pytest.raises(PetitionNotFoundError):
        service.sign(EMAIL_USER, "yok")


def test_should_store_signature_with_time_from_clock(repo, clock, petition):
    # Arrange: spy — gerçek repo'yu sarar, yapılan çağrıları kaydeder.
    spy = Mock(wraps=repo)
    service = SignatureService(spy, clock)

    # Act
    service.sign(EMAIL_USER, petition.id)

    # Assert
    spy.add_signature.assert_called_once_with(
        Signature(petition_id=petition.id, uid=EMAIL_USER.uid, signed_at=FIXED_NOW)
    )


def test_should_report_already_signed_when_repository_detects_race(repo, clock, petition):
    # Arrange: aynı anda iki istek — has_signed False dedi ama kayıt sırasında çakışma oldu.
    racy_repo = Mock(wraps=repo)
    racy_repo.add_signature.side_effect = AlreadySignedError()
    service = SignatureService(racy_repo, clock)

    # Act / Assert
    with pytest.raises(NotEligibleError) as excinfo:
        service.sign(EMAIL_USER, petition.id)

    assert excinfo.value.reason is SignBlockReason.ALREADY_SIGNED
