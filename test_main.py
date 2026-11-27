import main
from main import Direction, Game, GameStorage, Map, Player, EXIT_POSITION, START_POSITION
from pathlib import Path
import json

import pytest

MAZE = Path(main.__file__).parent / "maze.json"

SMALL = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
]

NORTH, EAST, SOUTH, WEST = Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST

def write_maze(folder: Path, grid, name="maze.json") -> Path:
    path = folder / name
    path.write_text(json.dumps({str(i): row for i, row in enumerate(grid)}), encoding="utf=8")
    return path

@pytest.fixture
def maze(tmp_path):
    return Map(write_maze(tmp_path, SMALL))

@pytest.fixture
def game(maze, tmp_path):
    return Game(maze, Player("Ann", 1, 3), (1, 1), tmp_path / "ann.json")


@pytest.fixture(scope="module")
def real_maze():
    return Map(MAZE)

def feed_input(monkeypatch, answers):
    """Make input() return the given answers in order (EOFError when exhausted)."""
    it = iter(answers)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    monkeypatch.setattr("builtins.input", fake_input)

def test_direction_default_is_north():
    assert Direction().name == "NORTH"
    
def test_direction_turn_right_full_circle():
    d, seen = Direction(), []
    for _ in range(4):
        d.turn_right()
        seen.append(d.name)
    assert seen == ["EAST", "SOUTH", "WEST", "NORTH"]
    
def test_direction_turn_left_full_circle():
    d, seen = Direction(), []
    for _ in range(4):
        d.turn_left()
        seen.append(d.name)
    assert seen == ["WEST", "SOUTH", "EAST", "NORTH"]
    
@pytest.mark.parametrize("start, expected", [
    (NORTH, "SOUTH"), (SOUTH, "NORTH"), (EAST, "WEST"), (WEST, "EAST"),
])
def test_direction_turn_back(start, expected):
    d = Direction(*start)
    d.turn_back()
    assert d.name == expected
    
@pytest.mark.parametrize("bad", [(1, 1), (0, 0), (2, 0), (0, -2)])
def test_direction_invalid_raises(bad):
    with pytest.raises(ValueError):
        Direction(*bad)
        
def test_map_dimensions_and_cells(maze):
    assert (maze.width, maze.height) == (5, 5)
    assert maze.get_cell(1, 1) == 0
    assert maze.get_cell(0, 0) == 1
    
@pytest.mark.parametrize("x, y", [(-1, 0), (0, -1), (5, 0), (0, 5), (99, 99)])
def test_map_out_of_bounds_is_wall(maze, x, y):
    assert maze.is_wall(x, y)
    assert not maze.is_valid_position(x, y)
    
def test_map_is_valid_position(maze):
    assert maze.is_valid_position(1, 1)
    assert not maze.is_valid_position(2, 2)
    
def test_map_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        Map(tmp_path / "nope.json")
        
@pytest.mark.parametrize("content", ["{not json", "{}", "[[1, 0]]", json.dumps({"0": [1, 1, 1], "1": [1, 1]}), json.dumps({"0": [1, 2, 1]}), json.dumps({"a": [1, 1]}),], ids=["bad_json", "empty", "list", "ragged", "bad_cell", "bad_key"])
def test_map_invalid_files(tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        Map(path)
        
def test_player_name_is_stripped():
    assert Player("  Ann  ", 1, 1).name == "Ann"
    
@pytest.mark.parametrize("bad", ["", "   ", None])
def test_player_empty_name_rejected(bad):
    with pytest.raises(ValueError):
        Player(bad, 1, 1)
        
def test_player_move_forward_into_open_cell(maze):
    p = Player("A", 1, 2)              # facing NORTH, (1, 1) is open
    assert p.move_forward(maze) is True
    assert p.position == (1, 1)
    assert p.moves == 1
    
def test_player_move_forward_blocked_by_wall(maze):
    p = Player("A", 1, 2)
    p.turn_right()                     # facing EAST, (2, 2) is a wall
    assert p.move_forward(maze) is False
    assert p.position == (1, 2)
    assert p.moves == 0
    
def test_player_cannot_walk_out_of_maze(maze):
    p = Player("A", 1, 1)
    p.turn_left()                      # WEST, (0, 1) is a wall
    assert p.move_forward(maze) is False
    assert p.position == (1, 1)
    
def test_player_turning_does_not_count_as_move():
    p = Player("A", 1, 2)
    p.turn_left()
    p.turn_right()
    p.turn_back()
    assert p.moves == 0
    
@pytest.mark.parametrize("facing, expected", [
    (NORTH, dict(front="Empty", right="Wall",  back="Empty", left="Wall")),
    (EAST,  dict(front="Wall",  right="Empty", back="Wall",  left="Empty")),
    (SOUTH, dict(front="Empty", right="Wall",  back="Empty", left="Wall")),
    (WEST,  dict(front="Wall",  right="Empty", back="Wall",  left="Empty")),
], ids=["north", "east", "south", "west"])
def test_player_look_around_for_every_facing(maze, facing, expected):
    p = Player("A", 1, 2, Direction(*facing))
    assert p.look_around(maze) == expected
    
def test_player_look_around_tells_left_from_right(maze):
    p = Player("A", 1, 1)              # facing NORTH, corner cell
    seen = p.look_around(maze)
    assert seen == dict(front="Wall", right="Empty", back="Empty", left="Wall")
    
def test_storage_save_and_load_roundtrip(maze, tmp_path):
    p = Player("Ann", 1, 3, Direction(*EAST), moves=7)
    path = tmp_path / "saves" / "ann.json"          # folder is created
    GameStorage.save_game(p, path)

    loaded = GameStorage.load_game(path, maze)
    assert loaded.name == "Ann"
    assert loaded.position == (1, 3)
    assert loaded.direction.name == "EAST"
    assert loaded.moves == 7
    
def test_storage_save_leaves_no_temp_file(tmp_path):
    GameStorage.save_game(Player("Ann", 1, 1), tmp_path / "ann.json")
    assert list(tmp_path.glob("*.tmp")) == []
    
def test_storage_load_missing_file(maze, tmp_path):
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
def test_storage_load_corrupt_saves(maze, tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content if isinstance(content, str) else json.dumps(content),
                    encoding="utf-8")
    with pytest.raises(ValueError):
        GameStorage.load_game(path, maze)
        
def test_game_get_save_path_valid(tmp_path):
    assert Game.get_save_path("Ann", tmp_path) == tmp_path / "Ann.json"
    
@pytest.mark.parametrize("bad", [
    "", "   ", "../evil", "a/b", "a\\b", "a:b", "a*b", "a?b", 'a"b',
    "a<b", "a>b", "a|b", "a.b", "tab\tname", None,
])
def test_game_get_save_path_rejects_bad_names(tmp_path, bad):
    with pytest.raises(ValueError):
        Game.get_save_path(bad, tmp_path)
        
def test_game_rejects_player_inside_wall(maze):
    with pytest.raises(ValueError):
        Game(maze, Player("A", 0, 0), (1, 1))
        
def test_game_rejects_exit_inside_wall(maze):
    with pytest.raises(ValueError):
        Game(maze, Player("A", 1, 1), (0, 0))
        

def test_game_turn_commands_and_lowercase_input(game):
    game.process_command("r")
    assert game.player.direction.name == "EAST"
    game.process_command(" L ")
    assert game.player.direction.name == "NORTH"
    game.process_command("B")
    assert game.player.direction.name == "SOUTH"
    
def test_game_forward_command_and_wall_message(game, capsys):
    game.process_command("F")
    assert "moved forward" in capsys.readouterr().out
    game.process_command("R")
    game.process_command("F")
    assert "wall is blocking" in capsys.readouterr().out
    
def test_game_invalid_command_keeps_game_running(game, capsys):
    assert game.process_command("xyz") is True
    assert "Invalid command" in capsys.readouterr().out
    
def test_game_quit_command_stops_game(game):
    assert game.process_command("q") is False
    
def test_game_save_command_writes_file(game, tmp_path):
    game.process_command("F")
    game.process_command("S")
    data = json.loads((tmp_path / "ann.json").read_text(encoding="utf-8"))
    assert (data["x"], data["y"], data["moves"]) == (1, 2, 1)
    
def test_game_save_command_without_save_path_does_not_crash(maze, capsys):
    game = Game(maze, Player("Ann", 1, 3), (1, 1))      # no save_path
    assert game.process_command("S") is True
    assert "not available" in capsys.readouterr().out
    
def test_game_show_surroundings_output(game, capsys):
    game.show_surroundings()
    out = capsys.readouterr().out
    assert "facing NORTH" in out
    assert "FRONT: Empty" in out
    assert "Moves: 0" in out
    
def test_game_play_until_win_deletes_save(game, monkeypatch, capsys):
    GameStorage.save_game(game.player, game.save_path)
    assert game.save_path.exists()

    feed_input(monkeypatch, ["F", "F"])
    game.play()

    assert game.check_win()
    assert "Congratulations" in capsys.readouterr().out
    assert not game.save_path.exists()
    
def test_game_quit_keeps_save_file(game, monkeypatch, capsys):
    GameStorage.save_game(game.player, game.save_path)
    feed_input(monkeypatch, ["Q"])
    game.play()
    assert "Game ended" in capsys.readouterr().out
    assert game.save_path.exists()
    
def test_game_end_of_input_acts_like_quit(game, monkeypatch):
    feed_input(monkeypatch, [])           
    game.play()                               
    assert not game.check_win()
    
def test_real_maze_shape_and_values(real_maze):
    assert (real_maze.width, real_maze.height) == (32, 32)
    assert all(c in (0, 1) for row in real_maze.grid for c in row)
    
def test_real_maze_exit_is_only_opening_in_outer_border(real_maze):
    border = [(x, y) for y in range(32) for x in range(32)
              if (x in (0, 31) or y in (0, 31)) and not real_maze.is_wall(x, y)]
    assert border == [EXIT_POSITION]
    assert EXIT_POSITION[1] == 0
    
def test_real_maze_start_and_exit_are_open(real_maze):
    assert not real_maze.is_wall(*START_POSITION)
    assert not real_maze.is_wall(*EXIT_POSITION)
    
def test_main_starts_new_game_and_quits(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(main, "SAVE_DIR", tmp_path)
    feed_input(monkeypatch, ["Tester", "Q"])
    main.main()
    assert "Welcome to ESCAPE THE MAZE, Tester!" in capsys.readouterr().out
    
def test_main_rejects_invalid_name(monkeypatch, capsys):
    feed_input(monkeypatch, ["../hack"])
    main.main()
    assert "Unable to start the game" in capsys.readouterr().out