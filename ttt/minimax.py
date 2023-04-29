from typing import Protocol

from ttt.ttt import Board, Move, Player, children


class Node(Protocol):
    def score(self) -> int:
        ...

    def completed(self) -> bool:
        ...


def minimax(
    board: Board, maximising_player: Player = Player.X
) -> tuple[Board, Move]:
    if board.is_terminal():
        return board, (-1, -1)

    if board.player == maximising_player:
        best_board = Board.from_string("ooo......")
        for child in children(board):
            best_board = max(best_board, minimax(child)[0])

    else:
        best_board = Board.from_string("xxx......")
        for child in children(board):
            best_board = min(best_board, minimax(child)[0])

    return best_board, best_board.moves[board.depth]
