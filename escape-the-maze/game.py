from pathlib import Path

import config
from maze import Map
from player import Player
from storage import GameStorage


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

        folder = config.SAVE_DIR if save_dir is None else Path(save_dir)
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
