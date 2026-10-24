"""T2.4 — Firebase token doğrulama (FirebaseTokenVerifier). Firebase yerine Mock kullanılır."""

from unittest.mock import Mock

import pytest

from app.auth.verifier import FirebaseTokenVerifier, InvalidTokenError
from app.domain.models import User


def test_should_map_firebase_claims_to_user():
    # Arrange
    claims = {
        "uid": "abc123",
        "email": "ayse@example.com",
        "email_verified": True,
        "phone_number": "+905551112233",
        "name": "Ayşe",
    }
    verifier = FirebaseTokenVerifier(verify_fn=Mock(return_value=claims))

    # Act
    user = verifier.verify("gecerli-token")

    # Assert
    assert user == User(
        uid="abc123",
        email="ayse@example.com",
        email_verified=True,
        phone_number="+905551112233",
        display_name="Ayşe",
    )


def test_should_use_defaults_when_optional_claims_are_missing():
    verifier = FirebaseTokenVerifier(verify_fn=Mock(return_value={"uid": "abc123"}))

    assert verifier.verify("gecerli-token") == User(uid="abc123")


def test_should_pass_token_to_firebase_exactly_once():
    verify_fn = Mock(return_value={"uid": "abc123"})
    verifier = FirebaseTokenVerifier(verify_fn=verify_fn)

    verifier.verify("gecerli-token")

    verify_fn.assert_called_once_with("gecerli-token")


def test_should_raise_invalid_token_when_firebase_rejects_token():
    verifier = FirebaseTokenVerifier(verify_fn=Mock(side_effect=ValueError("token expired")))

    with pytest.raises(InvalidTokenError):
        verifier.verify("suresi-dolmus-token")


def test_should_reject_empty_token_without_calling_firebase():
    verify_fn = Mock()
    verifier = FirebaseTokenVerifier(verify_fn=verify_fn)

    with pytest.raises(InvalidTokenError):
        verifier.verify("")

    verify_fn.assert_not_called()
