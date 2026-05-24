"""Core rules for Awalé / Oware Abapa.

The board is stored as 12 pits:
- player 0 owns pits 0..5
- player 1 owns pits 6..11
Sowing advances by increasing indexes modulo 12.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Iterable, List, Optional, Tuple


class Awale:
    """Encapsulates the whole game state and the legal moves.

    The class deliberately exposes copies of the board instead of the internal
    list, so callers cannot mutate the game state without using ``play``.
    """

    NB_PITS = 12
    PITS_PER_PLAYER = 6
    INITIAL_SEEDS = 4
    WIN_SCORE = 25
    MAX_SCORE = 48

    def __init__(self, board: Optional[Iterable[int]] = None,
                 scores: Optional[Iterable[int]] = None,
                 current_player: int = 0) -> None:
        self.__board: List[int] = list(board) if board is not None else [self.INITIAL_SEEDS] * self.NB_PITS
        self.__scores: List[int] = list(scores) if scores is not None else [0, 0]
        self.__current_player = current_player
        self.__history: List[Tuple[List[int], List[int], int]] = []
        self.__winner: Optional[int] = None
        self.__finished = False
        self.__validate_state()

    def __validate_state(self) -> None:
        if len(self.__board) != self.NB_PITS:
            raise ValueError("The board must contain 12 pits.")
        if len(self.__scores) != 2:
            raise ValueError("Scores must contain exactly two values.")
        if self.__current_player not in (0, 1):
            raise ValueError("Current player must be 0 or 1.")
        if any(seed < 0 for seed in self.__board + self.__scores):
            raise ValueError("Seeds and scores cannot be negative.")

    # ---------- Read-only accessors ----------
    def copy(self) -> "Awale":
        return Awale(self.__board, self.__scores, self.__current_player)

    def board(self) -> List[int]:
        return list(self.__board)

    def scores(self) -> Tuple[int, int]:
        return self.__scores[0], self.__scores[1]

    def current_player(self) -> int:
        return self.__current_player

    def opponent(self, player: Optional[int] = None) -> int:
        p = self.__current_player if player is None else player
        return 1 - p

    def finished(self) -> bool:
        if self.__finished:
            return True
        return self.winner() is not None or len(self.legal_moves()) == 0

    def winner(self) -> Optional[int]:
        if self.__winner is not None:
            return self.__winner
        if self.__scores[0] >= self.WIN_SCORE:
            return 0
        if self.__scores[1] >= self.WIN_SCORE:
            return 1
        if self.__scores[0] == 24 and self.__scores[1] == 24:
            return -1
        return None

    def side_indexes(self, player: int) -> range:
        return range(0, 6) if player == 0 else range(6, 12)

    def opponent_side_indexes(self, player: int) -> range:
        return self.side_indexes(1 - player)

    def seeds_on_side(self, player: int) -> int:
        return sum(self.__board[i] for i in self.side_indexes(player))

    # ---------- Move handling ----------
    def legal_moves(self, player: Optional[int] = None) -> List[int]:
        """Return pit indexes that are legal for ``player``.

        A legal move starts from a non-empty pit owned by the player. If the
        opponent has no seeds, the selected move must feed the opponent whenever
        at least one such move exists.
        """
        p = self.__current_player if player is None else player
        candidates = [i for i in self.side_indexes(p) if self.__board[i] > 0]
        if not candidates:
            return []

        opponent_empty = self.seeds_on_side(1 - p) == 0
        if not opponent_empty:
            return candidates

        feeding_moves = [move for move in candidates if self.__feeds_opponent(move, p)]
        return feeding_moves if feeding_moves else []

    def __feeds_opponent(self, pit: int, player: int) -> bool:
        seeds = self.__board[pit]
        pos = pit
        for _ in range(seeds):
            pos = (pos + 1) % self.NB_PITS
            if pos == pit:
                pos = (pos + 1) % self.NB_PITS
            if pos in self.opponent_side_indexes(player):
                return True
        return False

    def play(self, pit: int) -> int:
        """Play a move and return the number of captured seeds."""
        if self.__finished:
            raise ValueError("The game is already finished.")
        if pit not in self.legal_moves():
            raise ValueError(f"Illegal move: pit {pit}")

        self.__history.append((self.board(), list(self.__scores), self.__current_player))
        player = self.__current_player
        captured = self.__sow_and_capture(pit, player)
        self.__scores[player] += captured

        # If the next player cannot play and cannot be fed, collect remaining seeds.
        self.__current_player = 1 - player
        if not self.legal_moves(self.__current_player):
            self.__collect_remaining_seeds()
            self.__finished = True
        elif self.winner() is not None:
            self.__finished = True
        return captured

    def __sow_and_capture(self, pit: int, player: int) -> int:
        seeds = self.__board[pit]
        self.__board[pit] = 0
        pos = pit
        for _ in range(seeds):
            pos = (pos + 1) % self.NB_PITS
            if pos == pit:  # standard rule: do not sow into the original pit
                pos = (pos + 1) % self.NB_PITS
            self.__board[pos] += 1

        captured_pits: List[int] = []
        while pos in self.opponent_side_indexes(player) and self.__board[pos] in (2, 3):
            captured_pits.append(pos)
            pos = (pos - 1) % self.NB_PITS

        captured = sum(self.__board[i] for i in captured_pits)
        if not captured_pits:
            return 0

        # Starvation rule: do not perform a capture that empties the opponent side.
        opponent_after = self.seeds_on_side(1 - player) - captured
        if opponent_after == 0:
            return 0

        for i in captured_pits:
            self.__board[i] = 0
        return captured

    def __collect_remaining_seeds(self) -> None:
        for player in (0, 1):
            remaining = self.seeds_on_side(player)
            self.__scores[player] += remaining
            for pit in self.side_indexes(player):
                self.__board[pit] = 0

    def undo(self) -> None:
        if not self.__history:
            raise ValueError("No move to undo.")
        board, scores, current = self.__history.pop()
        self.__board = board
        self.__scores = scores
        self.__current_player = current
        self.__finished = False
        self.__winner = None

    def result_for(self, player: int) -> float:
        """Return 1.0 for win, 0.5 for draw, 0.0 for loss."""
        winner = self.winner()
        if winner is None and self.finished():
            if self.__scores[0] > self.__scores[1]:
                winner = 0
            elif self.__scores[1] > self.__scores[0]:
                winner = 1
            else:
                winner = -1
        if winner == -1:
            return 0.5
        return 1.0 if winner == player else 0.0

    def winner_by_score(self) -> int:
        if self.__scores[0] > self.__scores[1]:
            return 0
        if self.__scores[1] > self.__scores[0]:
            return 1
        return -1

    def pretty(self) -> str:
        top = " ".join(f"{self.__board[i]:2d}" for i in range(11, 5, -1))
        bottom = " ".join(f"{self.__board[i]:2d}" for i in range(0, 6))
        return (
            f"Scores: P0={self.__scores[0]} P1={self.__scores[1]} | "
            f"Turn: P{self.__current_player}\n"
            f"P1: {top}\n"
            f"P0: {bottom}"
        )

    def __repr__(self) -> str:
        return f"Awale(board={self.__board}, scores={self.__scores}, current_player={self.__current_player})"
