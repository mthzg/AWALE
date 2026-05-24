from __future__ import annotations

import math
import random
import time
from typing import Callable, List, Optional

from .core import Awale


class Player:
    def __init__(self, name: str, game: Optional[Awale] = None) -> None:
        self._name = name
        self._awale = game if game is not None else Awale()

    @property
    def name(self) -> str:
        return self._name

    @property
    def awale(self) -> Awale:
        return self._awale

    def set_game(self, game: Awale) -> None:
        self._awale = game

    def choose_move(self, game: Awale) -> int:
        raise NotImplementedError


class StupidBot(Player):
    def __init__(self, game: Optional[Awale] = None) -> None:
        super().__init__("Stupid Bot", game)

    def choose_move(self, game: Awale) -> int:
        self.set_game(game)
        return random.choice(game.legal_moves())


class GreedyTactic(Player):
    def __init__(self, game: Optional[Awale] = None) -> None:
        super().__init__("Greedy Tactic", game)

    def choose_move(self, game: Awale) -> int:
        self.set_game(game)
        player = game.current_player()
        scored = []
        for move in game.legal_moves():
            clone = game.copy()
            before = clone.scores()[player]
            clone.play(move)
            gain = clone.scores()[player] - before
            reserve = clone.seeds_on_side(player)
            scored.append((gain, reserve, random.random(), move))
        return max(scored)[3]


class Human(Player):

    def __init__(self, game: Optional[Awale] = None) -> None:
        super().__init__("Human", game)

    def choose_move(self, game: Awale) -> int:
        self.set_game(game)
        from .gui import AwaleGUI
        gui = AwaleGUI(game)
        return gui.ask_human_move()


class MinMax(Player):

    def __init__(self, depth: int = 4, heuristic: str = "score", game: Optional[Awale] = None) -> None:
        super().__init__(f"MinMax({heuristic}, d={depth})", game)
        self.__depth = depth
        self.__heuristic_name = heuristic
        self.__heuristics = {
            "score": self.__score_heuristic,
            "mobility": self.__mobility_heuristic,
        }
        if heuristic not in self.__heuristics:
            raise ValueError("heuristic must be 'score' or 'mobility'")

    def choose_move(self, game: Awale) -> int:
        self.set_game(game)
        player = game.current_player()
        best_value = -math.inf
        best_moves: List[int] = []
        alpha, beta = -math.inf, math.inf

        for move in game.legal_moves():
            child = game.copy()
            child.play(move)
            value = self.__alphabeta(child, self.__depth - 1, alpha, beta, player)
            if value > best_value:
                best_value = value
                best_moves = [move]
            elif value == best_value:
                best_moves.append(move)
            alpha = max(alpha, best_value)
        return random.choice(best_moves)

    def __alphabeta(self, game: Awale, depth: int, alpha: float, beta: float, root_player: int) -> float:
        if depth == 0 or game.finished():
            return self.__evaluate(game, root_player)

        legal = game.legal_moves()
        if not legal:
            return self.__evaluate(game, root_player)

        maximizing = game.current_player() == root_player
        if maximizing:
            value = -math.inf
            for move in legal:
                child = game.copy()
                child.play(move)
                value = max(value, self.__alphabeta(child, depth - 1, alpha, beta, root_player))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value

        value = math.inf
        for move in legal:
            child = game.copy()
            child.play(move)
            value = min(value, self.__alphabeta(child, depth - 1, alpha, beta, root_player))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

    def __evaluate(self, game: Awale, player: int) -> float:
        winner = game.winner()
        if game.finished() or winner is not None:
            result = game.result_for(player)
            if result == 1.0:
                return 10_000
            if result == 0.5:
                return 0
            return -10_000
        return self.__heuristics[self.__heuristic_name](game, player)

    def __score_heuristic(self, game: Awale, player: int) -> float:
        opponent = 1 - player
        scores = game.scores()
        return 5.0 * (scores[player] - scores[opponent]) + 0.2 * (game.seeds_on_side(player) - game.seeds_on_side(opponent))

    def __mobility_heuristic(self, game: Awale, player: int) -> float:
        opponent = 1 - player
        score_delta = game.scores()[player] - game.scores()[opponent]
        own_moves = len(game.legal_moves(player))
        opp_moves = len(game.legal_moves(opponent))
        own_seeds = game.seeds_on_side(player)
        opp_seeds = game.seeds_on_side(opponent)
        return 2.0 * score_delta + 1.5 * (own_moves - opp_moves) + 0.3 * (own_seeds - opp_seeds)


class Sommet:
    def __init__(self, game: Awale, parent: Optional["Sommet"] = None, move: Optional[int] = None) -> None:
        self._awale = game.copy()
        self.__parent = parent
        self.__move = move
        self.__children: List[Sommet] = []
        self.__untried_moves = self._awale.legal_moves()
        self.__visits = 0
        self.__wins = 0.0

    @property
    def awale(self) -> Awale:
        return self._awale

    @property
    def move(self) -> Optional[int]:
        return self.__move

    @property
    def visits(self) -> int:
        return self.__visits

    @property
    def wins(self) -> float:
        return self.__wins

    @property
    def children(self) -> List["Sommet"]:
        return list(self.__children)

    def fully_expanded(self) -> bool:
        return len(self.__untried_moves) == 0

    def expand(self) -> "Sommet":
        move = self.__untried_moves.pop(random.randrange(len(self.__untried_moves)))
        child_game = self._awale.copy()
        child_game.play(move)
        child = Sommet(child_game, self, move)
        self.__children.append(child)
        return child

    def best_child(self, temperature: float = math.sqrt(2.0)) -> "Sommet":
        if not self.__children:
            raise ValueError("No children available.")
        log_parent = math.log(max(1, self.__visits))

        def uct(child: Sommet) -> float:
            if child.__visits == 0:
                return math.inf
            exploitation = child.__wins / child.__visits
            exploration = temperature * math.sqrt(log_parent / child.__visits)
            return exploitation + exploration

        return max(self.__children, key=uct)

    def update(self, result: float) -> None:
        self.__visits += 1
        self.__wins += result

    def parent(self) -> Optional["Sommet"]:
        return self.__parent


class MCTS(Player):
    def __init__(self, iterations: int = 500, temperature: float = math.sqrt(2.0),
                 time_limit: Optional[float] = None, game: Optional[Awale] = None) -> None:
        super().__init__(f"MCTS({iterations})", game)
        self.__iterations = iterations
        self.__temperature = temperature
        self.__time_limit = time_limit

    def choose_move(self, game: Awale) -> int:
        self.set_game(game)
        root_player = game.current_player()
        root = Sommet(game)
        end_time = time.time() + self.__time_limit if self.__time_limit else None

        i = 0
        while i < self.__iterations and (end_time is None or time.time() < end_time):
            node = self.__select(root)
            if not node.awale.finished() and not node.fully_expanded():
                node = node.expand()
            result = self.__simulate(node.awale.copy(), root_player)
            self.__backpropagate(node, result)
            i += 1

        if not root.children:
            return random.choice(game.legal_moves())
        best = max(root.children, key=lambda child: child.visits)
        return int(best.move)

    def __select(self, node: Sommet) -> Sommet:
        while not node.awale.finished() and node.fully_expanded() and node.children:
            node = node.best_child(self.__temperature)
        return node

    def __simulate(self, game: Awale, root_player: int) -> float:
        safety = 0
        while not game.finished() and safety < 250:
            moves = game.legal_moves()
            if not moves:
                break
            game.play(random.choice(moves))
            safety += 1
        return game.result_for(root_player)

    def __backpropagate(self, node: Sommet, result: float) -> None:
        current: Optional[Sommet] = node
        while current is not None:
            current.update(result)
            current = current.parent()
