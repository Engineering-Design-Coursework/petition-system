"""T1.7 — Kampanya sayfaları (liste, oluştur, detay, ara). FastAPI TestClient ile.

Not: Bu testler T1.1–T1.6'yı kullanır; en son yapılacak Faz 1 görevidir.
Sayfalardaki data-* öznitelikleri (ör. data-error="title") testlerin okuduğu işaretlerdir.
"""

from datetime import timedelta

import pytest

from tests.helpers import (
    EMAIL_USER,
    FIXED_NOW,
    VALID_DESCRIPTION,
    VALID_GOAL,
    VALID_TITLE,
    login,
    make_petition,
)

# GÖREV T1.7 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T1.7 henüz yapılmadı")

VALID_FORM = {"title": VALID_TITLE, "description": VALID_DESCRIPTION, "goal": str(VALID_GOAL)}


# --- Listeleme -------------------------------------------------------------------


def test_list_should_show_empty_message_when_there_are_no_petitions(client):
    response = client.get("/petitions")

    assert response.status_code == 200
    assert "Henüz kampanya yok" in response.text


def test_list_should_show_petition_titles(client, repo):
    repo.add_petition(make_petition(title="Yemekhane fiyatları düşsün"))
    repo.add_petition(make_petition(title="Kütüphane 7/24 açık olsun"))

    response = client.get("/petitions")

    assert "Yemekhane fiyatları düşsün" in response.text
    assert "Kütüphane 7/24 açık olsun" in response.text


def test_home_should_show_recent_petitions(client, repo):
    repo.add_petition(make_petition(title="Yemekhane fiyatları düşsün"))

    assert "Yemekhane fiyatları düşsün" in client.get("/").text


# --- Oluşturma -------------------------------------------------------------------


def test_new_form_should_redirect_to_login_when_not_logged_in(client):
    response = client.get("/petitions/new", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"].startswith("/login?next=")


def test_new_form_should_render_when_logged_in(client):
    login(client)

    response = client.get("/petitions/new")

    assert response.status_code == 200
    assert 'name="title"' in response.text


def test_create_should_save_petition_and_redirect_to_it(client, repo):
    login(client)

    response = client.post("/petitions", data=VALID_FORM, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/petitions/1"
    saved = repo.get_petition("1")
    assert saved.title == VALID_TITLE
    assert saved.owner_uid == EMAIL_USER.uid


def test_create_should_redirect_to_login_and_save_nothing_when_not_logged_in(client, repo):
    response = client.post("/petitions", data=VALID_FORM, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")
    assert repo.list_recent() == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "kısa"),
        ("description", "çok kısa açıklama"),
        ("goal", "5"),
        ("goal", "abc"),
    ],
)
def test_create_should_show_error_and_keep_input_when_form_is_invalid(client, repo, field, value):
    login(client)
    form = {**VALID_FORM, field: value}

    response = client.post("/petitions", data=form)

    assert response.status_code == 400
    assert f'data-error="{field}"' in response.text
    assert value in response.text  # kullanıcının yazdığı kaybolmamalı
    assert repo.list_recent() == []


# --- Detay -----------------------------------------------------------------------


def test_detail_should_show_petition_with_progress_and_open_graph_tags(client, repo):
    repo.add_petition(make_petition(signature_count=25, goal=100))

    response = client.get("/petitions/1")

    assert response.status_code == 200
    assert VALID_TITLE in response.text
    assert VALID_DESCRIPTION in response.text
    assert 'data-count="25"' in response.text
    assert 'data-percent="25"' in response.text
    assert 'property="og:title"' in response.text
    assert 'content="http://testserver/petitions/1"' in response.text


def test_detail_should_escape_html_in_user_content(client, repo):
    # Güvenlik (XSS): kullanıcının yazdığı HTML/JS çalıştırılmamalı, düz metin gösterilmeli.
    repo.add_petition(make_petition(title="<script>alert(1)</script>"))

    response = client.get("/petitions/1")

    assert "<script>alert(1)</script>" not in response.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text


def test_detail_should_thank_user_after_signing(client, repo):
    repo.add_petition(make_petition())

    response = client.get("/petitions/1?signed=1")

    assert "İmzanız alındı" in response.text


def test_detail_should_return_404_when_petition_does_not_exist(client):
    assert client.get("/petitions/yok").status_code == 404


# --- Arama -----------------------------------------------------------------------


def test_search_should_list_only_matching_petitions(client, repo):
    repo.add_petition(make_petition(title="Kampüse bisiklet yolu yapılsın"))
    repo.add_petition(
        make_petition(
            title="Otopark ücretsiz olsun",
            description="Öğrenci otoparkı için ücret alınmamasını istiyoruz. " + "x" * 20,
            created_at=FIXED_NOW + timedelta(minutes=1),
        )
    )

    response = client.get("/search", params={"q": "kampus"})

    assert response.status_code == 200
    assert "Kampüse bisiklet yolu yapılsın" in response.text
    assert "Otopark ücretsiz olsun" not in response.text


def test_search_should_render_empty_page_without_query(client, repo):
    repo.add_petition(make_petition())

    response = client.get("/search")

    assert response.status_code == 200
    assert VALID_TITLE not in response.text
