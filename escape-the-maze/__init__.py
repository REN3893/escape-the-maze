"""ESCAPE THE MAZE - a terminal maze game."""
from .cli import main
from .direction import Direction
from .game import Game
from .maze import Map
from .player import Player
from .storage import GameStorage

__version__ = "1.0.0"
__all__ = ["Direction", "Game", "GameStorage", "Map", "Player", "main"]
