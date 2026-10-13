"""pytest fixture'ları: her test temiz bir sahte veritabanı ve sabit bir saat alır."""

import pytest
from fastapi.testclient import TestClient

from app.auth.verifier import StubTokenVerifier
from app.clock import FixedClock
from app.config import Settings
from app.main import create_app
from app.repositories.memory import InMemoryPetitionRepository
from tests.helpers import FIXED_NOW, TEST_TOKENS


@pytest.fixture
def clock():
    return FixedClock(FIXED_NOW)


@pytest.fixture
def repo():
    return InMemoryPetitionRepository()


@pytest.fixture
def settings():
    return Settings(base_url="http://testserver")


@pytest.fixture
def app(settings, repo, clock):
    return create_app(settings=settings, repo=repo, verifier=StubTokenVerifier(TEST_TOKENS), clock=clock)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client
