import json

import pytest

from escape_the_maze import Game, GameStorage, Player


def test_get_save_path_valid(tmp_path):
    assert Game.get_save_path("Ann", tmp_path) == tmp_path / "Ann.json"


@pytest.mark.parametrize("bad", [
    "", "   ", "../evil", "a/b", "a\\b", "a:b", "a*b", "a?b", 'a"b',
    "a<b", "a>b", "a|b", "a.b", "tab\tname", None,
])
def test_get_save_path_rejects_bad_names(tmp_path, bad):
    with pytest.raises(ValueError):
        Game.get_save_path(bad, tmp_path)


def test_rejects_player_inside_wall(maze):
    with pytest.raises(ValueError):
        Game(maze, Player("A", 0, 0), (1, 1))


def test_rejects_exit_inside_wall(maze):
    with pytest.raises(ValueError):
        Game(maze, Player("A", 1, 1), (0, 0))


def test_turn_commands_and_lowercase_input(game):
    game.process_command("r")
    assert game.player.direction.name == "EAST"
    game.process_command(" L ")
    assert game.player.direction.name == "NORTH"
    game.process_command("B")
    assert game.player.direction.name == "SOUTH"


def test_forward_command_and_wall_message(game, capsys):
    game.process_command("F")
    assert "moved forward" in capsys.readouterr().out
    game.process_command("R")
    game.process_command("F")
    assert "wall is blocking" in capsys.readouterr().out


def test_invalid_command_keeps_game_running(game, capsys):
    assert game.process_command("xyz") is True
    assert "Invalid command" in capsys.readouterr().out


def test_quit_command_stops_game(game):
    assert game.process_command("q") is False


def test_save_command_writes_file(game, tmp_path):
    game.process_command("F")
    game.process_command("S")
    data = json.loads((tmp_path / "ann.json").read_text(encoding="utf-8"))
    assert (data["x"], data["y"], data["moves"]) == (1, 2, 1)


def test_save_command_without_save_path_does_not_crash(maze, capsys):
    game = Game(maze, Player("Ann", 1, 3), (1, 1))      # no save_path
    assert game.process_command("S") is True
    assert "not available" in capsys.readouterr().out


def test_show_surroundings_output(game, capsys):
    game.show_surroundings()
    out = capsys.readouterr().out
    assert "facing NORTH" in out
    assert "FRONT: Empty" in out
    assert "Moves: 0" in out


def test_play_until_win_deletes_save(game, feed_input, capsys):
    GameStorage.save_game(game.player, game.save_path)
    assert game.save_path.exists()

    feed_input(["F", "F"])
    game.play()

    assert game.check_win()
    assert "Congratulations" in capsys.readouterr().out
    assert not game.save_path.exists()


def test_quit_keeps_save_file(game, feed_input, capsys):
    GameStorage.save_game(game.player, game.save_path)
    feed_input(["Q"])
    game.play()
    assert "Game ended" in capsys.readouterr().out
    assert game.save_path.exists()


def test_end_of_input_acts_like_quit(game, feed_input):
    feed_input([])                               # first input() raises EOFError
    game.play()                                  # must return, not raise
    assert not game.check_win()
