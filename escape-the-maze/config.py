"""Game settings."""
from pathlib import Path

MAZE_PATH = Path(__file__).parent / "data" / "maze.json"

# Save files go in a "json" folder inside the directory you run the game from.
SAVE_DIR = Path("json")

# (x, y): x = column, y = row. Row 0 is the BACK of the maze (the exit),
# the last row is the FRONT. The player starts facing NORTH (towards row 0).
START_POSITION = (30, 30)
EXIT_POSITION = (14, 0)
