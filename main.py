"""Command line entry point.

Examples:
    python main.py play --p0 minmax-score --p1 greedy
    python main.py tournament --games 100
"""

from __future__ import annotations

import argparse

from awale import GreedyTactic, Human, MCTS, MinMax, StupidBot, play_game
from awale.tournament import default_tournament


def build_player(name: str):
    if name == "human":
        return Human()
    if name == "random":
        return StupidBot()
    if name == "greedy":
        return GreedyTactic()
    if name == "minmax-score":
        return MinMax(depth=4, heuristic="score")
    if name == "minmax-mobility":
        return MinMax(depth=4, heuristic="mobility")
    if name == "mcts":
        return MCTS(iterations=500)
    raise ValueError(f"Unknown player: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Awalé mini-project")
    sub = parser.add_subparsers(dest="command", required=True)

    play = sub.add_parser("play")
    play.add_argument("--p0", default="human", choices=["human", "random", "greedy", "minmax-score", "minmax-mobility", "mcts"])
    play.add_argument("--p1", default="minmax-score", choices=["human", "random", "greedy", "minmax-score", "minmax-mobility", "mcts"])
    play.add_argument("--gui", action="store_true")

    tour = sub.add_parser("tournament")
    tour.add_argument("--games", type=int, default=20)

    args = parser.parse_args()
    if args.command == "play":
        winner, scores, game = play_game(build_player(args.p0), build_player(args.p1), graphical=args.gui)
        print(game.pretty())
        print(f"Winner: {'draw' if winner == -1 else 'P' + str(winner)} | Scores: {scores}")
    elif args.command == "tournament":
        results = default_tournament(args.games)
        for duel, stats in results.items():
            print(f"\n{duel}")
            for key, value in stats.items():
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
