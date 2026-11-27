from collections import deque

import pytest

from escape_the_maze import Direction, Game, Map, Player
from escape_the_maze.config import EXIT_POSITION, MAZE_PATH, START_POSITION

NORTH, EAST, SOUTH, WEST = Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST


@pytest.fixture(scope="module")
def real_maze():
    return Map(MAZE_PATH)


def test_shape_and_values(real_maze):
    assert (real_maze.width, real_maze.height) == (32, 32)
    assert all(c in (0, 1) for row in real_maze.grid for c in row)


def test_exit_is_only_opening_in_outer_border(real_maze):
    border = [(x, y) for y in range(32) for x in range(32)
              if (x in (0, 31) or y in (0, 31)) and not real_maze.is_wall(x, y)]
    assert border == [EXIT_POSITION]
    assert EXIT_POSITION[1] == 0                 # exit is on the back row


def test_start_and_exit_are_open(real_maze):
    assert not real_maze.is_wall(*START_POSITION)
    assert not real_maze.is_wall(*EXIT_POSITION)


def test_solvable_by_playing_commands(real_maze):
    # Find the shortest path with BFS...
    queue = deque([START_POSITION])
    came_from = {START_POSITION: None}
    while queue:
        cell = queue.popleft()
        if cell == EXIT_POSITION:
            break
        for dx, dy in (NORTH, EAST, SOUTH, WEST):
            nxt = (cell[0] + dx, cell[1] + dy)
            if nxt not in came_from and not real_maze.is_wall(*nxt):
                came_from[nxt] = cell
                queue.append(nxt)
    assert EXIT_POSITION in came_from
    path, cell = [], EXIT_POSITION
    while cell is not None:
        path.append(cell)
        cell = came_from[cell]
    path.reverse()

    # ...then walk it using only the game's own commands.
    game = Game(real_maze, Player("Tester", *START_POSITION), EXIT_POSITION)
    right_of = {NORTH: EAST, EAST: SOUTH, SOUTH: WEST, WEST: NORTH}
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        wanted = (x2 - x1, y2 - y1)
        current = (game.player.direction.x, game.player.direction.y)
        if wanted == right_of[current]:
            game.process_command("R")
        elif current == right_of[wanted]:
            game.process_command("L")
        elif wanted != current:
            game.process_command("B")
        game.process_command("F")

    assert game.check_win()
    assert game.player.moves == len(path) - 1
