import json
from pathlib import Path

from direction import Direction
from maze import Map
from player import Player


class GameStorage:

    @staticmethod
    def save_game(player: Player, file_path: str | Path) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        save_data = {
            "name": player.name,
            "x": player.x,
            "y": player.y,
            "direction": [player.direction.x, player.direction.y],
            "moves": player.moves
        }

        # write to a temp file first so a crash can't corrupt the old save
        temp_path = path.with_suffix(path.suffix + ".tmp")
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(save_data, file, indent=4)
        temp_path.replace(path)

    @staticmethod
    def load_game(file_path: str | Path, maze: Map) -> Player:
        path = Path(file_path)
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Can't find file {path}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON")

        try:
            name = data["name"]
            x = data["x"]
            y = data["y"]
            dx, dy = data["direction"]
            moves = data.get("moves", 0)
        except (KeyError, TypeError, ValueError):
            raise ValueError("The save file is damaged or incomplete")

        numbers = (x, y, dx, dy, moves)
        if not all(type(n) is int for n in numbers) or moves < 0:
            raise ValueError("The save file contains invalid numbers")

        player = Player(name, x, y, Direction(dx, dy), moves)

        if maze.is_wall(player.x, player.y):
            raise ValueError("The saved position is inside a wall")

        return player
