import json

import pytest

from escape_the_maze import Map


def test_dimensions_and_cells(maze):
    assert (maze.width, maze.height) == (5, 5)
    assert maze.get_cell(1, 1) == 0
    assert maze.get_cell(0, 0) == 1


@pytest.mark.parametrize("x, y", [(-1, 0), (0, -1), (5, 0), (0, 5), (99, 99)])
def test_out_of_bounds_is_wall(maze, x, y):
    assert maze.is_wall(x, y)
    assert not maze.is_valid_position(x, y)


def test_is_valid_position(maze):
    assert maze.is_valid_position(1, 1)
    assert not maze.is_valid_position(2, 2)


def test_rows_are_sorted_numerically(tmp_path, write_maze):
    # With 12 rows a plain string sort would put "10" and "11" before "2".
    grid = [[1, 1, 1] for _ in range(12)]
    grid[10] = [1, 0, 1]
    tall = Map(write_maze(tmp_path, grid, "tall.json"))
    assert tall.grid[10] == [1, 0, 1]
    assert tall.grid[2] == [1, 1, 1]


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        Map(tmp_path / "nope.json")


@pytest.mark.parametrize("content", [
    "{not json",                                   # bad json
    "{}",                                          # empty
    "[[1, 0]]",                                    # list instead of dict
    json.dumps({"0": [1, 1, 1], "1": [1, 1]}),     # ragged rows
    json.dumps({"0": [1, 2, 1]}),                  # cell not 0/1
    json.dumps({"a": [1, 1]}),                     # non-numeric row key
], ids=["bad_json", "empty", "list", "ragged", "bad_cell", "bad_key"])
def test_invalid_files(tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        Map(path)
