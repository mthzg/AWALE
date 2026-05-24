from .core import Awale
from .players import GreedyTactic, Human, MCTS, MinMax, Player, Sommet, StupidBot
from .match import play_game

__all__ = [
    "Awale", "Player", "Human", "StupidBot", "GreedyTactic",
    "MinMax", "Sommet", "MCTS", "play_game",
]
