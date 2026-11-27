from escape_the_maze import cli, config


def test_main_starts_new_game_and_quits(tmp_path, monkeypatch, feed_input, capsys):
    monkeypatch.setattr(config, "SAVE_DIR", tmp_path)
    feed_input(["Tester", "Q"])
    cli.main()
    assert "Welcome to ESCAPE THE MAZE, Tester!" in capsys.readouterr().out


def test_main_rejects_invalid_name(feed_input, capsys):
    feed_input(["../hack"])
    cli.main()
    assert "Unable to start the game" in capsys.readouterr().out


def test_main_resumes_saved_game(tmp_path, monkeypatch, feed_input, capsys):
    monkeypatch.setattr(config, "SAVE_DIR", tmp_path)
    # first session: move one step forward, save, quit
    feed_input(["Tester", "F", "S", "Q"])
    cli.main()
    assert (tmp_path / "Tester.json").exists()
    capsys.readouterr()
    # second session: resume and check the move counter was restored
    feed_input(["Tester", "y", "Q"])
    cli.main()
    assert "Moves: 1" in capsys.readouterr().out
