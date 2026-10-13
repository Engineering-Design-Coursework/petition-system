"""T1.2 — Form doğrulama (validate_petition_input). Denklik sınıfları (EP) + sınır değer analizi (BVA)."""

import pytest

from app.domain.validation import (
    DESCRIPTION_MAX,
    DESCRIPTION_MIN,
    GOAL_MAX,
    GOAL_MIN,
    TITLE_MAX,
    TITLE_MIN,
    validate_petition_input,
)
from tests.helpers import VALID_DESCRIPTION, VALID_GOAL, VALID_TITLE

# GÖREV T1.2 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T1.2 henüz yapılmadı")


def test_should_return_no_errors_when_all_fields_are_valid():
    assert validate_petition_input(VALID_TITLE, VALID_DESCRIPTION, VALID_GOAL) == {}


@pytest.mark.parametrize(
    ("length", "is_valid"),
    [
        (0, False),
        (TITLE_MIN - 1, False),
        (TITLE_MIN, True),
        (TITLE_MIN + 1, True),
        (TITLE_MAX - 1, True),
        (TITLE_MAX, True),
        (TITLE_MAX + 1, False),
    ],
)
def test_should_check_title_length_boundaries(length, is_valid):
    errors = validate_petition_input("a" * length, VALID_DESCRIPTION, VALID_GOAL)

    assert ("title" not in errors) is is_valid


@pytest.mark.parametrize(
    ("length", "is_valid"),
    [
        (DESCRIPTION_MIN - 1, False),
        (DESCRIPTION_MIN, True),
        (DESCRIPTION_MIN + 1, True),
        (DESCRIPTION_MAX - 1, True),
        (DESCRIPTION_MAX, True),
        (DESCRIPTION_MAX + 1, False),
    ],
)
def test_should_check_description_length_boundaries(length, is_valid):
    errors = validate_petition_input(VALID_TITLE, "a" * length, VALID_GOAL)

    assert ("description" not in errors) is is_valid


@pytest.mark.parametrize(
    ("goal", "is_valid"),
    [
        (-5, False),
        (0, False),
        (GOAL_MIN - 1, False),
        (GOAL_MIN, True),
        (GOAL_MIN + 1, True),
        (GOAL_MAX - 1, True),
        (GOAL_MAX, True),
        (GOAL_MAX + 1, False),
    ],
)
def test_should_check_goal_boundaries(goal, is_valid):
    errors = validate_petition_input(VALID_TITLE, VALID_DESCRIPTION, goal)

    assert ("goal" not in errors) is is_valid


def test_should_reject_title_when_it_is_only_spaces():
    errors = validate_petition_input(" " * 20, VALID_DESCRIPTION, VALID_GOAL)

    assert "title" in errors


@pytest.mark.parametrize(
    ("title", "is_valid"),
    [
        pytest.param("  " + "a" * TITLE_MIN + "  ", True, id="bosluklar-sayilmaz-gecerli"),
        pytest.param("  " + "a" * (TITLE_MIN - 1) + "  ", False, id="bosluklar-sayilmaz-kisa"),
    ],
)
def test_should_measure_length_after_stripping_spaces(title, is_valid):
    errors = validate_petition_input(title, VALID_DESCRIPTION, VALID_GOAL)

    assert ("title" not in errors) is is_valid


def test_should_report_only_the_invalid_field():
    errors = validate_petition_input("kısa", VALID_DESCRIPTION, VALID_GOAL)

    assert set(errors) == {"title"}


def test_should_report_every_invalid_field_at_once():
    errors = validate_petition_input("", "", 0)

    assert set(errors) == {"title", "description", "goal"}
    assert all(isinstance(message, str) and message for message in errors.values())
