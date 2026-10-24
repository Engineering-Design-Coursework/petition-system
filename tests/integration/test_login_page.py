"""T2.7 — Firebase giriş sayfası (login.html, auth.js). Gerçek Firebase'e bağlanmaz."""

import pytest
from fastapi.testclient import TestClient

from app.auth.verifier import StubTokenVerifier
from app.config import Settings
from app.main import create_app
from tests.helpers import TEST_TOKENS

WEB_CONFIG = {
    "apiKey": "test-api-key",
    "authDomain": "test.firebaseapp.com",
    "projectId": "test",
    "appId": "1:2:web:3",
}


@pytest.fixture
def firebase_client(repo, clock):
    # Arrange: Firebase ayarlı ama sahte verifier ile
    settings = Settings(firebase_web_config=WEB_CONFIG, firebase_credentials="test-key.json")
    app = create_app(settings=settings, repo=repo, verifier=StubTokenVerifier(TEST_TOKENS), clock=clock)
    with TestClient(app) as client:
        yield client


def test_should_load_auth_script_when_firebase_is_configured(firebase_client):
    response = firebase_client.get("/login")

    assert response.status_code == 200
    assert "/static/js/auth.js" in response.text


def test_should_pass_web_config_and_next_to_script(firebase_client):
    response = firebase_client.get("/login?next=/petitions/1")

    assert "test-api-key" in response.text
    assert 'data-next="/petitions/1"' in response.text


def test_should_offer_email_and_phone_forms(firebase_client):
    response = firebase_client.get("/login")

    assert "data-email-form" in response.text
    assert "data-phone-form" in response.text


def test_should_hide_demo_users_when_firebase_is_configured(firebase_client):
    response = firebase_client.get("/login")

    assert 'name="id_token"' not in response.text


def test_should_ignore_external_next_url(firebase_client):
    response = firebase_client.get("/login?next=https://kotu-site.com")

    assert 'data-next="/"' in response.text


def test_should_serve_auth_script(firebase_client):
    assert firebase_client.get("/static/js/auth.js").status_code == 200


def test_should_not_load_auth_script_in_demo_mode(client):
    assert "/static/js/auth.js" not in client.get("/login").text
