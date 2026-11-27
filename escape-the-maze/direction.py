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
