import main
from main import Direction, Game, GameStorage, Map, Player, EXIT_POSITION, START_POSITION
from pathlib import Path
import json

MAZE = Path(main.__file__).parent / "maze.json"

def write_maze(folder: Path, grid, name="maze.json") -> Path:
    path = folder / name
    path.write_text(json.dumps({str(i): row for i, row in enumerate(grid)}), encoding="utf=8")
    return path

