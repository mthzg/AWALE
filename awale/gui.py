from __future__ import annotations

import tkinter as tk
from typing import Optional

from .core import Awale


class AwaleGUI:
    def __init__(self, game: Awale) -> None:
        self.__game = game
        self.__root = tk.Tk()
        self.__root.title("Awalé")
        self.__selected: Optional[int] = None
        self.__buttons = []
        self.__status = tk.StringVar()
        self.__build()
        self.refresh()

    def __build(self) -> None:
        title = tk.Label(self.__root, text="Awalé / Oware Abapa", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=6, pady=10)

        for col, pit in enumerate(range(11, 5, -1)):
            button = tk.Button(self.__root, width=8, height=3, command=lambda p=pit: self.__select(p))
            button.grid(row=1, column=col, padx=4, pady=4)
            self.__buttons.append((pit, button))

        for col, pit in enumerate(range(0, 6)):
            button = tk.Button(self.__root, width=8, height=3, command=lambda p=pit: self.__select(p))
            button.grid(row=2, column=col, padx=4, pady=4)
            self.__buttons.append((pit, button))

        tk.Label(self.__root, textvariable=self.__status, font=("Arial", 12)).grid(row=3, column=0, columnspan=6, pady=10)

    def __select(self, pit: int) -> None:
        if pit in self.__game.legal_moves():
            self.__selected = pit
            self.__root.quit()

    def refresh(self) -> None:
        board = self.__game.board()
        legal = set(self.__game.legal_moves())
        for pit, button in self.__buttons:
            owner = 0 if pit < 6 else 1
            button.config(
                text=f"P{owner}\ncase {pit}\n{board[pit]}",
                state=(tk.NORMAL if pit in legal else tk.DISABLED),
            )
        s0, s1 = self.__game.scores()
        self.__status.set(f"Tour: joueur {self.__game.current_player()} | Scores: P0={s0}, P1={s1}")
        self.__root.update_idletasks()
        self.__root.update()

    def ask_human_move(self) -> int:
        self.__selected = None
        self.refresh()
        self.__root.mainloop()
        if self.__selected is None:
            raise RuntimeError("No move selected.")
        return self.__selected

    def close(self) -> None:
        self.__root.destroy()
