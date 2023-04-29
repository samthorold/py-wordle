from __future__ import annotations
from enum import Enum
from typing import Iterator

from minimax import minimax

Move = tuple[str, str, str, str, str]


class Player(Enum):
    X = "x"
    O = "o"


class Board:
    @classmethod
    def from_string(
        cls,
        string: str,
        player: Player = Player.X,
        depth: int = 0,
    ) -> Board:
        ...

    def __init__(
        self,
        state: list[Move],
        player: Player,
        moves: list[Move] | None = None,
        depth: int = 0,
    ):
        self.board = state
        self.player = player
        self.moves: list[Move] = [] if moves is None else moves
        self.depth = depth

    def __gt__(self, other: Board) -> bool:
        return self.score() > other.score()

    def __lt__(self, other: Board) -> bool:
        return self.score() < other.score()

    def is_maximising(self) -> bool:
        return self.player == Player.X

    def minimum(self) -> Board:
        return Board.from_string("ooo......")

    def maximum(self) -> Board:
        return Board.from_string("xxx......")

    def __str__(self) -> str:
        return "\n".join([str(row) for row in self.board])

    def move(self, move: Move) -> Board:
        next_board = [row for row in self.board]
        next_board.append(move)
        return Board(
            state=next_board,
            player=self.next_player(),
            moves=self.moves + [move],
            depth=self.depth + 1,
        )

    def score(self) -> int:
        ...

    def is_terminal(self) -> bool:
        ...

    def next_player(self) -> Player:
        return Player.X if self.player == Player.O else Player.O

    def children(self) -> Iterator[Board]:
        if self.is_terminal():
            return
        yield self
