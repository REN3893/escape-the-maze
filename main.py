import json
from pathlib import Path

SAVE_DIR = Path(__file__).parent / "json"

START_POSITION = (30, 30)
EXIT_POSITION = (14, 0)


class Direction:

    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    def __init__(self, x: int = 0, y: int = -1):
        if (x, y) not in [self.NORTH, self.EAST, self.SOUTH, self.WEST]:
            raise ValueError("The direction is incorrect")
        self.x = x
        self.y = y

    def turn_left(self) -> None:
        self.x, self.y = self.y, -self.x

    def turn_right(self) -> None:
        self.x, self.y = -self.y, self.x

    def turn_back(self) -> None:
        self.x, self.y = -self.x, -self.y

    @property
    def name(self) -> str:
        names = {
            self.NORTH: "NORTH",
            self.EAST: "EAST",
            self.SOUTH: "SOUTH",
            self.WEST: "WEST"
        }
        return names[(self.x, self.y)]


class Map:
    def __init__(self, file_path: str | Path):
        self.file_path = file_path
        self.grid = self._load_maze()
        self.height = len(self.grid)
        self.width = len(self.grid[0])

    def _load_maze(self) -> list[list[int]]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Maze not found on {self.file_path}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

        if not isinstance(data, dict) or not data:
            raise ValueError("The JSON is empty")

        try:
            # sort numerically so that row "10" comes after row "9"
            row_keys = sorted(data.keys(), key=int)
        except ValueError:
            raise ValueError("Row keys must be numbers")

        grid = [data[key] for key in row_keys]

        if not all(isinstance(row, list) and row for row in grid):
            raise ValueError("Every row must be a non-empty list")
        if len({len(row) for row in grid}) != 1:
            raise ValueError("All rows must have the same length")
        if any(cell not in (0, 1) for row in grid for cell in row):
            raise ValueError("Cells must be 0 (path) or 1 (wall)")

        return grid

    def get_cell(self, x: int, y: int) -> int:
        if not (0 <= y < self.height and 0 <= x < self.width):
            return 1
        return self.grid[y][x]

    def is_wall(self, x: int, y: int) -> bool:
        return self.get_cell(x, y) == 1

    def is_valid_position(self, x: int, y: int) -> bool:
        return not self.is_wall(x, y)


class Player:
    def __init__(self, name: str, x: int, y: int,
                 direction: Direction | None = None, moves: int = 0):
        self.name = name
        self.x = x
        self.y = y
        self.direction = direction if direction is not None else Direction()
        self.moves = moves

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or len(value.strip()) < 1:
            raise ValueError("Name length cannot be less than 1 character")
        self._name = value.strip()

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

    def turn_left(self) -> None:
        self.direction.turn_left()

    def turn_right(self) -> None:
        self.direction.turn_right()

    def turn_back(self) -> None:
        self.direction.turn_back()

    def move_forward(self, maze: Map) -> bool:
        next_x = self.x + self.direction.x
        next_y = self.y + self.direction.y

        if maze.is_wall(next_x, next_y):
            return False

        self.x = next_x
        self.y = next_y
        self.moves += 1
        return True

    def look_around(self, maze: Map) -> dict[str, str]:
        dx, dy = self.direction.x, self.direction.y
        surround = {
            "front": (dx, dy),
            "right": (-dy, dx),
            "back": (-dx, -dy),
            "left": (dy, -dx)
        }

        observe = {}
        for side, (sx, sy) in surround.items():
            if maze.is_wall(self.x + sx, self.y + sy):
                observe[side] = "Wall"
            else:
                observe[side] = "Empty"

        return observe


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


class Game:

    def __init__(self, maze: Map, player: Player, exit: tuple[int, int],
                 save_path: str | Path | None = None):
        if maze.is_wall(*exit):
            raise ValueError("The exit is inside a wall")
        if maze.is_wall(*player.position):
            raise ValueError("The player starts inside a wall")

        self.maze = maze
        self.player = player
        self.exit = exit
        self.save_path = Path(save_path) if save_path is not None else None

    @staticmethod
    def get_save_path(name: str, save_dir: str | Path | None = None) -> Path:
        forbidden = ['.', '/', chr(92), ':', '*', '?', '"', '<', '>', '|']
        if (not isinstance(name, str) or not name.strip()
                or any(char in forbidden or ord(char) < 32 for char in name)):
            raise ValueError("The name is invalid")

        folder = SAVE_DIR if save_dir is None else Path(save_dir)
        return folder / f"{name}.json"

    def show_surroundings(self) -> None:
        observe = self.player.look_around(self.maze)
        print(f"\nYou are facing {self.player.direction.name}.")
        print(f"  FRONT: {observe['front']}")
        print(f"  LEFT:  {observe['left']}")
        print(f"  RIGHT: {observe['right']}")
        print(f"  BACK:  {observe['back']}")
        print(f"Moves: {self.player.moves}")

    def check_win(self) -> bool:
        return self.player.position == self.exit

    def process_command(self, command: str) -> bool:
        command = command.strip().upper()

        if command == "L":
            self.player.turn_left()
            print(f"You turned left. Now facing {self.player.direction.name}.")
        elif command == "R":
            self.player.turn_right()
            print(f"You turned right. Now facing {self.player.direction.name}.")
        elif command == "B":
            self.player.turn_back()
            print(f"You turned back. Now facing {self.player.direction.name}.")
        elif command == "F":
            if self.player.move_forward(self.maze):
                print("You moved forward.")
            else:
                print("A wall is blocking your way.")
        elif command == "S":
            if self.save_path is None:
                print("Saving is not available in this game.")
            else:
                try:
                    GameStorage.save_game(self.player, self.save_path)
                    print("Game saved.")
                except OSError as error:
                    print(f"Could not save the game: {error}")
        elif command == "Q":
            return False
        else:
            print("Invalid command. Enter L, R, B, F, S, or Q.")

        return True

    def play(self) -> None:
        print(f"\nWelcome to ESCAPE THE MAZE, {self.player.name}!")
        print("Find the exit using only the information around you.")

        while not self.check_win():
            self.show_surroundings()
            print("\n[L] Turn left  [R] Turn right  [B] Turn back  [F] Move forward  [S] Save  [Q] Quit")
            try:
                command = input("> ")
            except EOFError:
                command = "Q"

            if not self.process_command(command):
                print("Game ended. Your progress is not lost if you saved.")
                return

        print(f"\nCongratulations! You escaped the maze in {self.player.moves} moves.")
        if self.save_path is not None:
            try:
                self.save_path.unlink(missing_ok=True)
            except OSError:
                pass


def main() -> None:
    maze_path = Path(__file__).parent / "maze.json"

    try:
        maze = Map(maze_path)
        name = input("Enter your player name: ").strip()
        save_path = Game.get_save_path(name)

        if save_path.exists():
            answer = input(f"A saved game for {name} was found. Resume? (y/n): ").strip().lower()
        else:
            answer = "n"

        if answer == "y":
            player = GameStorage.load_game(save_path, maze)
        else:
            player = Player(name, *START_POSITION)

        game = Game(maze, player, EXIT_POSITION, save_path)
        game.play()

    except (OSError, ValueError) as error:
        print(f"Unable to start the game: {error}")


if __name__ == "__main__":
    main()