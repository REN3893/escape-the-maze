import json
from pathlib import Path

class Direction:
    
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)
    
    def __init__(self, x: int = 0, y: int = -1):
        self.x = x
        self.y = y
        if (self.x, self.y) not in [self.NORTH, self.EAST, self.SOUTH, self.WEST]:
            raise ValueError("The direction is incorrect")
        
    def turn_left(self):
        self.x, self.y = self.y, -self.x
        
    def turn_right(self):
        self.x, self.y = -self.y, self.x
        
    def turn_back(self):
        self.x, self.y = -self.y, -self.x
        
    @property
    def name(self) -> str:
        names = {
            self.NORTH: "NORTH",
            self.EAST: "EAST",
            self.SOUTH: "SOUTH",
            self.WEST: "WEST"
        }
        return names[(self.x, self.y)]

    

class Player:
    def __init__(self):
        
        self.direction = Direction()
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value: str):
        if len(value) < 1:
            raise NameError("Name length cannot be less than 1 character")
        self._name = value
    
class Map:
    def __init__(self, file_path: str | Path):
        self.file_path = file_path
        self.grid
        
    def _lode_maze(self) -> list[list[int]]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Maze not found on {self.file_path}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        
        if not isinstance(data, dict) or not data:
            raise ValueError("The JSON is empty")
        
        row_keys = list(data.keys())
        grid = [data[key] for key in row_keys]
        
        return grid
        
        
