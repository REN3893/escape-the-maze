from direction import Direction
from maze import Map


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
