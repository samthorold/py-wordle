from wordle.board import Board
from wordle.settings import Settings


def wordle(words: set[str], aim: str, settings: Settings | None = None) -> Board:
    if settings is None:
        settings = Settings()

    if aim not in words:
        raise ValueError("Aim not in words, might struggle.")

    board = Board(
        words=words,
        moves=[],
        statuses=[],
        num_guesses=settings.num_guesses,
        guess_len=settings.guess_len,
    )

    while True:
        board = board.guess()
        board = board.evaluate(aim)
        if board.is_terminal():
            break
    return board
