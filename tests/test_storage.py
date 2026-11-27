import json

import pytest

from escape_the_maze import Direction, GameStorage, Player


def test_save_and_load_roundtrip(maze, tmp_path):
    p = Player("Ann", 1, 3, Direction(*Direction.EAST), moves=7)
    path = tmp_path / "saves" / "ann.json"          # folder is created
    GameStorage.save_game(p, path)

    loaded = GameStorage.load_game(path, maze)
    assert loaded.name == "Ann"
    assert loaded.position == (1, 3)
    assert loaded.direction.name == "EAST"
    assert loaded.moves == 7


def test_save_leaves_no_temp_file(tmp_path):
    GameStorage.save_game(Player("Ann", 1, 1), tmp_path / "ann.json")
    assert list(tmp_path.glob("*.tmp")) == []


def test_load_missing_file(maze, tmp_path):
    with pytest.raises(FileNotFoundError):
        GameStorage.load_game(tmp_path / "none.json", maze)


GOOD_SAVE = {"name": "Ann", "x": 1, "y": 1, "direction": [0, -1], "moves": 0}


@pytest.mark.parametrize("content", [
    "{oops",
    "[1, 2]",
    {k: v for k, v in GOOD_SAVE.items() if k != "x"},
    {**GOOD_SAVE, "direction": [1, 1]},
    {**GOOD_SAVE, "direction": [1]},
    {**GOOD_SAVE, "x": "1"},
    {**GOOD_SAVE, "moves": -3},
    {**GOOD_SAVE, "name": "  "},
    {**GOOD_SAVE, "x": 0, "y": 0},
    {**GOOD_SAVE, "x": 50, "y": 50},
], ids=["not_json", "not_dict", "missing_key", "bad_direction", "short_direction",
        "text_position", "negative_moves", "empty_name", "inside_wall", "outside_maze"])
def test_load_corrupt_saves(maze, tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content if isinstance(content, str) else json.dumps(content),
                    encoding="utf-8")
    with pytest.raises(ValueError):
        GameStorage.load_game(path, maze)
