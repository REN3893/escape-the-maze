import pytest

from escape_the_maze import Direction, Player

NORTH, EAST, SOUTH, WEST = Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST


def test_name_is_stripped():
    assert Player("  Ann  ", 1, 1).name == "Ann"


@pytest.mark.parametrize("bad", ["", "   ", None])
def test_empty_name_rejected(bad):
    with pytest.raises(ValueError):
        Player(bad, 1, 1)


def test_move_forward_into_open_cell(maze):
    p = Player("A", 1, 2)              # facing NORTH, (1, 1) is open
    assert p.move_forward(maze) is True
    assert p.position == (1, 1)
    assert p.moves == 1


def test_move_forward_blocked_by_wall(maze):
    p = Player("A", 1, 2)
    p.turn_right()                     # facing EAST, (2, 2) is a wall
    assert p.move_forward(maze) is False
    assert p.position == (1, 2)
    assert p.moves == 0


def test_cannot_walk_out_of_maze(maze):
    p = Player("A", 1, 1)
    p.turn_left()                      # WEST, (0, 1) is a wall
    assert p.move_forward(maze) is False
    assert p.position == (1, 1)


def test_turning_does_not_count_as_move():
    p = Player("A", 1, 2)
    p.turn_left()
    p.turn_right()
    p.turn_back()
    assert p.moves == 0


# Player at (1, 2): open to the NORTH and SOUTH, walls to the EAST and WEST.
@pytest.mark.parametrize("facing, expected", [
    (NORTH, dict(front="Empty", right="Wall",  back="Empty", left="Wall")),
    (EAST,  dict(front="Wall",  right="Empty", back="Wall",  left="Empty")),
    (SOUTH, dict(front="Empty", right="Wall",  back="Empty", left="Wall")),
    (WEST,  dict(front="Wall",  right="Empty", back="Wall",  left="Empty")),
], ids=["north", "east", "south", "west"])
def test_look_around_for_every_facing(maze, facing, expected):
    p = Player("A", 1, 2, Direction(*facing))
    assert p.look_around(maze) == expected


def test_look_around_tells_left_from_right(maze):
    p = Player("A", 1, 1)              # facing NORTH, corner cell
    assert p.look_around(maze) == dict(front="Wall", right="Empty",
                                       back="Empty", left="Wall")
