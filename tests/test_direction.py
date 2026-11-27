import pytest

from escape_the_maze import Direction

NORTH, EAST, SOUTH, WEST = Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST


def test_default_is_north():
    assert Direction().name == "NORTH"


def test_turn_right_full_circle():
    d, seen = Direction(), []
    for _ in range(4):
        d.turn_right()
        seen.append(d.name)
    assert seen == ["EAST", "SOUTH", "WEST", "NORTH"]


def test_turn_left_full_circle():
    d, seen = Direction(), []
    for _ in range(4):
        d.turn_left()
        seen.append(d.name)
    assert seen == ["WEST", "SOUTH", "EAST", "NORTH"]


@pytest.mark.parametrize("start, expected", [
    (NORTH, "SOUTH"), (SOUTH, "NORTH"), (EAST, "WEST"), (WEST, "EAST"),
])
def test_turn_back(start, expected):
    d = Direction(*start)
    d.turn_back()
    assert d.name == expected


@pytest.mark.parametrize("bad", [(1, 1), (0, 0), (2, 0), (0, -2)])
def test_invalid_direction_raises(bad):
    with pytest.raises(ValueError):
        Direction(*bad)
