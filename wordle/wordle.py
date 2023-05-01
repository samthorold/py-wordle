from wordle.board import Board
from wordle.settings import Settings


def wordle(
    words: set[str],
    aim: str,
    initial_guess: str,
    soft: bool,
) -> Board:
    if aim not in words:
        raise ValueError("Aim not in words, might struggle.")

    board = Board(
        words=words,
        moves=[],
        statuses=[],
        initial_guess=initial_guess,
    )

    while True:
        board = board.guess(soft)
        board = board.evaluate(aim)
        print(board)
        if board.is_terminal():
            break
    return board
