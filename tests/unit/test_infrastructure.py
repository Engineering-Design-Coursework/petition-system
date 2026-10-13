"""Hazır altyapı parçalarının testleri (saat, stub doğrulayıcı, ayarlar, yönlendirme güvenliği).

Bu dosyadaki testler en baştan yeşildir; bir değişiklik bunları kırarsa altyapı bozulmuş demektir.
"""

import pytest

from app.auth.verifier import InvalidTokenError, StubTokenVerifier
from app.clock import FixedClock
from app.config import DEFAULT_SECRET_KEY, load_settings
from app.routes.deps import safe_next
from tests.helpers import EMAIL_USER, FIXED_NOW

# --- FixedClock ------------------------------------------------------------------


def test_fixed_clock_should_return_same_time_until_advanced():
    clock = FixedClock(FIXED_NOW)

    assert clock.now() == clock.now() == FIXED_NOW

    clock.advance(60)
    assert (clock.now() - FIXED_NOW).total_seconds() == 60


# --- StubTokenVerifier -----------------------------------------------------------


def test_stub_verifier_should_return_known_user():
    assert StubTokenVerifier({"t": EMAIL_USER}).verify("t") == EMAIL_USER


def test_stub_verifier_should_reject_unknown_token():
    with pytest.raises(InvalidTokenError):
        StubTokenVerifier({"t": EMAIL_USER}).verify("bilinmeyen")


# --- load_settings ---------------------------------------------------------------

FIREBASE_ENV = {
    "FIREBASE_API_KEY": "key",
    "FIREBASE_AUTH_DOMAIN": "demo.firebaseapp.com",
    "FIREBASE_PROJECT_ID": "demo",
    "FIREBASE_APP_ID": "1:2:web:3",
    "FIREBASE_CREDENTIALS": "service-account.json",
}


def test_settings_should_default_to_demo_mode_when_env_is_empty():
    settings = load_settings({})

    assert settings.app_env == "dev"
    assert settings.use_firebase is False
    assert settings.secret_key == DEFAULT_SECRET_KEY


def test_settings_should_enable_firebase_when_credentials_and_api_key_exist():
    settings = load_settings(FIREBASE_ENV)

    assert settings.use_firebase is True
    assert settings.firebase_web_config["projectId"] == "demo"


def test_settings_should_strip_trailing_slash_from_base_url():
    assert load_settings({"BASE_URL": "https://example.com/"}).base_url == "https://example.com"


@pytest.mark.parametrize(
    "env",
    [
        pytest.param({"APP_ENV": "prod", **FIREBASE_ENV}, id="secret-key-yok"),
        pytest.param({"APP_ENV": "prod", "SECRET_KEY": "s3cr3t"}, id="firebase-yok"),
    ],
)
def test_settings_should_refuse_unsafe_production_config(env):
    with pytest.raises(RuntimeError):
        load_settings(env)


# --- safe_next (open redirect koruması) ------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("/petitions/1", "/petitions/1"),
        ("/", "/"),
        (None, "/"),
        ("", "/"),
        ("https://kotu-site.com", "/"),
        ("//kotu-site.com", "/"),
        ("/\\kotu-site.com", "/"),
    ],
)
def test_safe_next_should_only_allow_local_paths(value, expected):
    assert safe_next(value) == expected
