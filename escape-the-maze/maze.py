import json
from pathlib import Path


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
        # anything outside of the maze counts as a wall
        if not (0 <= y < self.height and 0 <= x < self.width):
            return 1
        return self.grid[y][x]

    def is_wall(self, x: int, y: int) -> bool:
        return self.get_cell(x, y) == 1

    def is_valid_position(self, x: int, y: int) -> bool:
        return not self.is_wall(x, y)
