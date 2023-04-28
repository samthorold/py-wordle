"""Tic-tac-toe implementation in Python to learn minimax."""

from __future__ import annotations
from enum import Enum
import sys
from typing import Iterator


class IllegalMove(Exception):
    """Cell contains a move already."""


class Player(Enum):
    X = "x"
    O = "o"


Move = tuple[Player, int, int]


class Board:
    @classmethod
    def from_string(cls, string: str) -> Board:
        state = "." * 9 if string is None else string
        state = state.lower()
        b: list[list[Player | None]] = []
        for r in range(3):
            b.append([])
            for c in range(3):
                ch = state[r * 3 + c]
                b[-1].append(Player(ch) if ch != "." else None)
        return cls(b)

    def __init__(self, state: list[list[Player | None]]):
        self.board = state

    def string(self) -> str:
        s = ""
        for row in self.board:
            for val in row:
                s += "." if val is None else val.value
            s += "\n"
        return s

    def move(self, move: Move) -> Board:
        pl, rix, cix = move
        if self.board[rix][cix]:
            raise IllegalMove(
                f"row={rix}, col={cix} is occupied ({self.board[rix][cix]})"
            )
        next_board = [[v for v in row] for row in self.board]
        next_board[rix][cix] = pl
        return Board(next_board)

    def score(self) -> int:
        for p in Player:
            sign = 1 if p == Player.X else -1
            if any(all(c == p for c in row) for row in self.board):
                return sign * 1
            if any(
                all(c == p for c in [self.board[i][j] for i in range(3)])
                for j in range(3)
            ):
                return sign * 1
            if all(
                [self.board[0][0] == p, self.board[1][1] == p, self.board[2][2] == p]
            ):
                return sign * 1
            if all(
                [self.board[2][0] == p, self.board[1][1] == p, self.board[0][2] == p]
            ):
                return sign * 1
        return 0

    def completed(self) -> bool:
        return all(all(row) for row in self.board)


def next_player(pl: Player) -> Player:
    return Player.X if pl == Player.O else Player.X


def children(
    board: Board,
    turn: Player,
    depth: int = 0,
) -> Iterator[tuple[Board, Move, int, int]]:
    # if the board is full or the last player just won
    current_score = board.score()
    if current_score or board.completed():
        return
    for rix, row in enumerate(board.board):
        for cix, val in enumerate(row):
            if val:
                continue
            move = (turn, rix, cix)
            next_board = board.move(move)
            current_score = next_board.score()
            yield next_board, move, depth, current_score


# def tree(
#     board: Board,
#     turn: Player,
#     depth: int = 0,
# ) -> Iterator[tuple[Board, Move, int, int]]:
#     for child in children(board=board, turn=turn, depth=depth):
#         yield child
#         yield from tree(board=child[0], turn=next_player(turn), depth=depth + 1)


def minimax(
    board: Board, pl: Player, depth: int = 0
) -> tuple[Board, Move, int, int]:
    if board.completed():
        return board, (pl, -1, -1), depth, 0

    best_board = Board([[]])
    best_move = (Player.X, -1, -1)
    best_depth = -1

    # maximising player
    if pl == Player.X:
        best_score = -10
        for child in children(board, pl, depth):
            if child[-1]:
                candidate = child
            else:
                candidate = minimax(child[0], next_player(pl), depth + 1)
            if candidate[-1] > best_score:
                *_, best_score = candidate
                best_board, best_move, *_ = child

    # minimising player
    elif pl == Player.O:
        best_score = 10
        for child in children(board, pl, depth):
            if child[-1]:
                candidate = child
            else:
                candidate = minimax(child[0], next_player(pl), depth + 1)
            if candidate[-1] < best_score:
                # best_board, best_move, best_depth, best_score = candidate
                *_, best_score = candidate
                best_board, best_move, *_ = child

    else:
        raise ValueError(f"Unknown player {pl}.")

    return best_board, best_move, best_depth, best_score


def main() -> int:
    board = Board.from_string("." * 9)
    while True:
        p = Player.O
        r, c = [int(m) for m in input("Move: ")]
        board = board.move((p, r, c))
        print(board.string())
        s = board.score()
        if s or board.completed():
            print(s)
            break
        p = Player.X
        _, (_, r, c), *_ = minimax(board, p)
        board = board.move((p, r, c))
        print(board.string())
        s = board.score()
        if s or board.completed():
            print(s)
            break
    return 0


if __name__ == "__main__":
    # board = new_board("x..oo....")
    # print(score(board, "x"))
    # print(string(board))

    # move = minimax(board, "x")
    # print(move)
    # print(string(move[0]))

    code = main()
    sys.exit(code)
