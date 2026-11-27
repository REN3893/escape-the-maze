import config
from game import Game
from maze import Map
from player import Player
from storage import GameStorage


def main() -> None:
    try:
        maze = Map(config.MAZE_PATH)
        name = input("Enter your player name: ").strip()
        save_path = Game.get_save_path(name)

        if save_path.exists():
            answer = input(f"A saved game for {name} was found. Resume? (y/n): ").strip().lower()
        else:
            answer = "n"

        if answer == "y":
            player = GameStorage.load_game(save_path, maze)
        else:
            player = Player(name, *config.START_POSITION)

        game = Game(maze, player, config.EXIT_POSITION, save_path)
        game.play()

    except (OSError, ValueError) as error:
        print(f"Unable to start the game: {error}")

if __name__ == "__main__":
    main()