"""T2.5 — İmza atma, canlı ilerleme, paylaşım (sayfa seviyesinde).

Not: Bu testler T1.x ve T2.1–T2.3'ü kullanır; en son yapılacak Faz 2 görevidir.
"""

import pytest

from app.domain.models import PetitionStatus
from tests.helpers import login, make_petition

# GÖREV T2.5 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T2.5 henüz yapılmadı")


@pytest.fixture
def petition(repo):
    return repo.add_petition(make_petition(goal=10))


def _sign(client, petition_id="1"):
    return client.post(f"/petitions/{petition_id}/sign", follow_redirects=False)


def test_sign_should_redirect_to_login_when_not_logged_in(client, repo, petition):
    response = _sign(client)

    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=/petitions/1"
    assert repo.get_petition("1").signature_count == 0


@pytest.mark.parametrize("token", ["token-email", "token-phone"])
def test_sign_should_count_signature_of_verified_user(client, repo, petition, token):
    login(client, token)

    response = _sign(client)

    assert response.status_code == 303
    assert response.headers["location"] == "/petitions/1?signed=1"
    assert repo.get_petition("1").signature_count == 1


def test_sign_should_return_409_when_user_signs_twice(client, repo, petition):
    login(client)
    _sign(client)

    response = _sign(client)

    assert response.status_code == 409
    assert "zaten imzaladınız" in response.text
    assert repo.get_petition("1").signature_count == 1


def test_sign_should_return_403_when_user_is_not_verified(client, repo, petition):
    login(client, "token-unverified")

    response = _sign(client)

    assert response.status_code == 403
    assert "doğrulayın" in response.text
    assert repo.get_petition("1").signature_count == 0


def test_sign_should_return_409_when_petition_is_closed(client, repo):
    repo.add_petition(make_petition(status=PetitionStatus.CLOSED))
    login(client)

    response = _sign(client)

    assert response.status_code == 409
    assert "kapalı" in response.text


def test_sign_should_return_404_when_petition_does_not_exist(client):
    login(client)

    assert _sign(client, "yok").status_code == 404


def test_progress_fragment_should_show_live_numbers_without_page_layout(client, repo):
    repo.add_petition(make_petition(goal=10, signature_count=4))

    response = client.get("/petitions/1/progress")

    assert response.status_code == 200
    assert 'data-count="4"' in response.text
    assert 'data-percent="40"' in response.text
    assert "<nav" not in response.text  # sadece parça, tüm sayfa değil


def test_progress_fragment_should_increase_after_signing(client, petition):
    login(client)
    _sign(client)

    assert 'data-percent="10"' in client.get("/petitions/1/progress").text


def test_detail_should_show_share_links_for_the_petition(client, petition):
    response = client.get("/petitions/1")

    assert "https://x.com/intent/tweet" in response.text
    assert "https://wa.me/" in response.text
    assert "http%3A%2F%2Ftestserver%2Fpetitions%2F1" in response.text


def test_progress_fragment_should_return_404_for_unknown_petition(client):
    assert client.get("/petitions/yok/progress").status_code == 404
