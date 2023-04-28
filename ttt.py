"""Tic-tac-toe implementation in Python to learn minimax."""

from __future__ import annotations
from enum import Enum
import logging
import sys
from typing import Iterator


logger = logging.getLogger(__name__)


class IllegalMove(Exception):
    """Cell contains a move already."""


class Player(Enum):
    X = "x"
    O = "o"


Move = tuple[int, int]


class Board:
    @classmethod
    def from_string(
        cls,
        string: str,
        player: Player = Player.O,
        depth: int = 0,
    ) -> Board:
        state = "." * 9 if string is None else string
        state = state.lower()
        b: list[list[Player | None]] = []
        for r in range(3):
            b.append([])
            for c in range(3):
                ch = state[r * 3 + c]
                b[-1].append(Player(ch) if ch != "." else None)
        return cls(b, player=player, depth=depth)

    def __init__(
        self,
        state: list[list[Player | None]],
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

    def string(self) -> str:
        s = f"{self.player} to play ...\n"
        for row in self.board:
            for val in row:
                s += "." if val is None else val.value
            s += "\n"
        s += f"{self.score()}\n"
        return s

    def move(self, move: Move) -> Board:
        rix, cix = move
        if self.board[rix][cix]:
            msg = f"row={rix}, col={cix} is occupied ({self.board[rix][cix]})"
            logger.error(msg)
            raise IllegalMove(msg)
        next_board = [[v for v in row] for row in self.board]
        next_board[rix][cix] = self.player
        logger.debug("%s %s %s", self.player, rix, cix)
        return Board(
            state=next_board,
            player=self.next_player(),
            moves=self.moves + [move],
            depth=self.depth + 1,
        )

    def score(self) -> int:
        for p in Player:
            sign = 1 if p == Player.X else -1
            if any(all(c == p for c in row) for row in self.board):
                return sign * (10 - self.depth)
            if any(
                all(c == p for c in [self.board[i][j] for i in range(3)])
                for j in range(3)
            ):
                return sign * (10 - self.depth)
            if all(
                [self.board[0][0] == p, self.board[1][1] == p, self.board[2][2] == p]
            ):
                return sign * (10 - self.depth)
            if all(
                [self.board[2][0] == p, self.board[1][1] == p, self.board[0][2] == p]
            ):
                return sign * (10 - self.depth)
        return 0

    def completed(self) -> bool:
        return all(all(row) for row in self.board)

    def next_player(self) -> Player:
        return Player.X if self.player == Player.O else Player.O


def children(board: Board) -> Iterator[Board]:
    # if the board is full or the last player just won
    if board.score() or board.completed():
        return
    for rix, row in enumerate(board.board):
        for cix, val in enumerate(row):
            if val:
                continue
            yield board.move((rix, cix))


def minimax(board: Board) -> Board:
    if board.score() or board.completed():
        return board

    # maximising player
    if board.player == Player.X:
        best_board = Board.from_string("ooo......")
        for child in children(board):
            best_board = max(best_board, minimax(child))

    # minimising player
    elif board.player == Player.O:
        best_board = Board.from_string("xxx......")
        for child in children(board):
            best_board = min(best_board, minimax(child))

    else:
        raise ValueError(f"Unknown player {board.player}.")

    return best_board


def main() -> int:
    logging.basicConfig(level=logging.WARNING)
    board = Board.from_string("." * 9, Player.O)
    while True:
        r, c = [int(m) for m in input("Move: ")]
        board = board.move((r, c))
        logger.info("%s %s", board.next_player(), board.moves[-1])
        print(board.string())
        s = board.score()
        if s or board.completed():
            print(s)
            break
        variation = minimax(board)
        print(variation.string())
        print(variation.moves)
        move = variation.moves[board.depth]
        logger.info("%s %s", board.next_player(), move)
        board = board.move(move)
        print(board.string())
        s = board.score()
        if s or board.completed():
            print(s)
            break
    return 0


if __name__ == "__main__":
    # board = Board.from_string(".........", Player.O)
    # board = board.move((1, 1))
    # print(board.string())
    # variation = minimax(board)
    # print(variation.string())
    # print(variation.moves, board.depth)

    # move = minimax(board, "x")
    # print(move)
    # print(string(move[0]))

    code = main()
    sys.exit(code)
