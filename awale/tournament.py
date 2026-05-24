"""Tournament/statistics runner for the concours part."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Tuple

from .match import play_game
from .players import GreedyTactic, MCTS, MinMax, Player, StupidBot

PlayerFactory = Callable[[], Player]


def run_duel(factory_a: PlayerFactory, factory_b: PlayerFactory, games: int = 100) -> Dict[str, int]:
    stats = defaultdict(int)
    for i in range(games):
        if i % 2 == 0:
            p0, p1 = factory_a(), factory_b()
            a_is = 0
        else:
            p0, p1 = factory_b(), factory_a()
            a_is = 1
        winner, scores, _ = play_game(p0, p1, graphical=False)
        if winner == -1:
            stats["draws"] += 1
        elif winner == a_is:
            stats["A_wins"] += 1
        else:
            stats["B_wins"] += 1
        stats[f"start_{a_is}_games"] += 1
    return dict(stats)


def default_tournament(games_per_duel: int = 20) -> Dict[str, Dict[str, int]]:
    # The default is intentionally 20 so it runs quickly. Use --games 100 for the assignment report.
    duels: Dict[str, Tuple[PlayerFactory, PlayerFactory]] = {
        "MinMax score vs Stupid Bot": (lambda: MinMax(depth=4, heuristic="score"), StupidBot),
        "Stupid Bot vs Greedy Tactic": (StupidBot, GreedyTactic),
        "MCTS vs MinMax mobility": (lambda: MCTS(iterations=250), lambda: MinMax(depth=3, heuristic="mobility")),
        "Greedy Tactic vs MinMax score": (GreedyTactic, lambda: MinMax(depth=3, heuristic="score")),
    }
    return {name: run_duel(a, b, games_per_duel) for name, (a, b) in duels.items()}
