import json
from pathlib import Path

import pytest

from escape_the_maze import Game, Map, Player

# Small 5x5 maze used by most tests ('#' = 1, '.' = 0):
#   #####
#   #...#
#   #.#.#      player at (1, 2) has walls EAST and WEST, paths NORTH and SOUTH
#   #...#
#   #####
SMALL = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
]


@pytest.fixture
def write_maze():
    """Return a function that writes a grid to a maze JSON file."""
    def _write(folder: Path, grid, name="maze.json") -> Path:
        path = folder / name
        path.write_text(json.dumps({str(i): row for i, row in enumerate(grid)}),
                        encoding="utf-8")
        return path
    return _write


@pytest.fixture
def maze(tmp_path, write_maze):
    return Map(write_maze(tmp_path, SMALL))


@pytest.fixture
def game(maze, tmp_path):
    # Player at (1, 3) facing NORTH; the exit (1, 1) is two steps ahead.
    return Game(maze, Player("Ann", 1, 3), (1, 1), tmp_path / "ann.json")


@pytest.fixture
def feed_input(monkeypatch):
    """Return a function that makes input() give the answers in order
    (and raise EOFError once they run out)."""
    def _feed(answers):
        it = iter(answers)

        def fake_input(prompt=""):
            try:
                return next(it)
            except StopIteration:
                raise EOFError
        monkeypatch.setattr("builtins.input", fake_input)
    return _feed
