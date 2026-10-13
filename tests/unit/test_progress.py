"""T1.3 — İlerleme yüzdesi (progress_percent). BVA: 0, hedefin hemen altı, tam hedef, hedefin üstü."""

import pytest

from app.domain.progress import is_goal_reached, progress_percent

# GÖREV T1.3 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T1.3 henüz yapılmadı")


@pytest.mark.parametrize(
    ("count", "goal", "expected"),
    [
        (0, 100, 0),
        (1, 100, 1),
        (50, 100, 50),
        (99, 100, 99),
        (100, 100, 100),
        (101, 100, 100),
        (150, 100, 100),
        (1, 3, 33),
        (2, 3, 66),  # aşağı yuvarlama: 66.67 -> 66
        (999, 1000, 99),  # hedefe ulaşmadan 100 görünmemeli
        (9, 10, 90),
    ],
)
def test_should_return_floored_percent_capped_at_100(count, goal, expected):
    # Act
    result = progress_percent(count, goal)

    # Assert
    assert result == expected
    assert isinstance(result, int)


@pytest.mark.parametrize(("count", "goal"), [(-1, 100), (0, 0), (5, -10)])
def test_should_raise_value_error_when_input_is_invalid(count, goal):
    with pytest.raises(ValueError):
        progress_percent(count, goal)


@pytest.mark.parametrize(
    ("count", "goal", "expected"),
    [(0, 10, False), (99, 100, False), (100, 100, True), (101, 100, True)],
)
def test_should_tell_whether_goal_is_reached(count, goal, expected):
    assert is_goal_reached(count, goal) is expected
