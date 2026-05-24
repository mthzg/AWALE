"""Game orchestration utilities."""

from __future__ import annotations

import time
from typing import Optional, Tuple

from .core import Awale
from .players import Human, Player
from .gui import AwaleGUI


def play_game(player0: Player, player1: Player, graphical: bool = False,
              delay: float = 0.25, max_turns: int = 300) -> Tuple[int, Tuple[int, int], Awale]:
    game = Awale()
    players = [player0, player1]
    gui: Optional[AwaleGUI] = AwaleGUI(game) if graphical else None

    turns = 0
    while not game.finished() and turns < max_turns:
        current = game.current_player()
        for p in players:
            p.set_game(game)

        if graphical and gui is not None and isinstance(players[current], Human):
            move = gui.ask_human_move()
        else:
            move = players[current].choose_move(game.copy())

        game.play(move)
        turns += 1

        if graphical and gui is not None:
            gui.refresh()
            print(game.pretty(), "\n")
            time.sleep(delay)

    if gui is not None:
        gui.refresh()

    if turns >= max_turns and not game.finished():
        # Defensive stop for abnormal loops; the board state remains inspectable.
        pass
    return game.winner_by_score(), game.scores(), game
