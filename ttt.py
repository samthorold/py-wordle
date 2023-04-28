"""Tic-tac-toe implementation in Python to learn minimax."""

from copy import deepcopy
import sys
from typing import Iterator, Literal


Player = Literal["x", "o", "."]

Board = list[list[Player]]

Move = tuple[Player, int, int]


def next_player(pl: Player) -> Player:
    return "x" if pl.lower() == "o" else "o"


def new_board(state: str | None = None) -> Board:
    state = "." * 9 if state is None else state.lower()
    b = []
    for r in range(3):
        b.append([])
        for c in range(3):
            b[-1].append(state[r * 3 + c])
    return b


def string(board: Board) -> str:
    s = ""
    for row in board:
        for val in row:
            s += val
        s += "\n"
    return s


def children(
    board: Board,
    turn: Player,
    depth: int = 0,
) -> Iterator[tuple[Board, Move, int, int]]:
    # if the board is full or the last player just won
    current_score = score(b=board, pl=next_player(turn))
    if current_score or completed(board):
        return
    for rix, row in enumerate(board):
        for cix, val in enumerate(row):
            if not val == ".":
                continue
            next_board: Board = [[v for v in row] for row in board]
            next_board[rix][cix] = turn
            move = (turn, rix, cix)
            current_score = score(b=next_board, pl=turn)
            yield next_board, move, depth, current_score


def tree(
    board: Board,
    turn: Player,
    depth: int = 0,
) -> Iterator[tuple[Board, Move, int, int]]:
    for child in children(board=board, turn=turn, depth=depth):
        yield child
        yield from tree(board=child[0], turn=next_player(turn), depth=depth + 1)


def score(b: Board, pl: Player) -> int:
    sign = 1 if pl == "x" else -1
    for p in ["x", "o"]:
        if any(all(c == p for c in row) for row in b):
            return sign * 1
        if any(all(c == p for c in [b[i][j] for i in range(3)]) for j in range(3)):
            return sign * 1
        if all([b[0][0] == p, b[1][1] == p, b[2][2] == p]):
            return sign * 1
        if all([b[2][0] == p, b[1][1] == p, b[0][2] == p]):
            return sign * 1
    return 0


def completed(b: Board) -> bool:
    return all(all(v != "." for v in row) for row in b)


def minimax(
    board: Board, pl: Player, depth: int = 0
) -> tuple[Board, Move, int, int]:
    if completed(board):
        return board, (pl, -1, -1), depth, 0

    best_board = new_board()
    best_move = ("x", -1, -1)
    best_depth = -1

    # maximising player
    if pl == "x":
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
    elif pl == "o":
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
    board = new_board()
    while True:
        p = "o"
        r, c = [int(m) for m in input("Move: ")]
        board[r][c] = p
        print(string(board))
        s = score(board, "x")
        if s or completed(board):
            print(s)
            break
        p = "x"
        _, (_, mr, mc), *_ = minimax(board, p)
        board[mr][mc] = p
        print(string(board))
        s = score(board, "o")
        if s or completed(board):
            print(s)
            break
    return 0


if __name__ == "__main__":
    board = new_board("x..oo....")
    # print(score(board, "x"))
    # print(string(board))

    # move = minimax(board, "x")
    # print(move)
    # print(string(move[0]))

    code = main()
    sys.exit(code)
