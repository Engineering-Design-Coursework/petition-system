"""Hazır rotaların entegrasyon testleri (ana sayfa, sağlık, giriş/çıkış). En baştan yeşildir."""

from tests.helpers import EMAIL_USER, login


def test_health_should_report_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_should_render_navbar_and_call_to_action(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Kampanya başlat" in response.text
    assert 'href="/login"' in response.text


def test_static_css_should_be_served(client):
    assert client.get("/static/css/style.css").status_code == 200


def test_login_page_should_offer_demo_users_when_firebase_is_not_configured(client):
    response = client.get("/login?next=/petitions/1")

    assert response.status_code == 200
    assert 'name="id_token"' in response.text
    assert 'value="/petitions/1"' in response.text


def test_form_login_should_redirect_to_next_and_remember_user(client):
    response = client.post(
        "/session", data={"id_token": "token-email", "next": "/search"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/search"
    assert EMAIL_USER.email in client.get("/").text


def test_form_login_should_ignore_external_next_url(client):
    response = client.post(
        "/session",
        data={"id_token": "token-email", "next": "https://kotu-site.com"},
        follow_redirects=False,
    )

    assert response.headers["location"] == "/"


def test_form_login_should_fail_with_invalid_token(client):
    response = client.post("/session", data={"id_token": "sahte"}, follow_redirects=False)

    assert response.status_code == 401
    assert "Giriş başarısız" in response.text


def test_json_login_should_return_204_for_valid_token(client):
    assert client.post("/session", json={"id_token": "token-phone"}).status_code == 204


def test_json_login_should_return_401_for_invalid_token(client):
    assert client.post("/session", json={"id_token": "sahte"}).status_code == 401


def test_logout_should_forget_user(client):
    login(client)

    response = client.post("/logout", follow_redirects=False)

    assert response.status_code == 303
    assert EMAIL_USER.email not in client.get("/").text
