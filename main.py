from enum import Enum
import random
from typing import Optional, Sequence

import structlog
import typer


logger = structlog.get_logger()


WORD_LEN = 5

with open("words.txt") as fh:
    WORDS = fh.read().splitlines()


class LSTAT(Enum):
    MISSING = "."
    PRESENT = "-"
    CORRECT = "="
    UNKNOWN = " "


class Guesses:
    def __init__(
        self,
        word: str,
        guesses: list[str] | None = None,
        statuses: list[list[LSTAT]] | None = None,
    ):
        self.word = word
        self.guesses: list[str] = [] if guesses is None else guesses
        self.statuses: list[list[LSTAT]] = [] if statuses is None else statuses

    def __len__(self) -> int:
        return len(self.guesses)

    def __str__(self) -> str:
        return "\n".join(
            ["".join(f"{s.value}" for s in status) for status in self.statuses]
        )

    def add(self, guess: str) -> None:
        status: list[LSTAT] = []
        for l, r in zip(guess, self.word):
            if l == r:
                status.append(LSTAT.CORRECT)
            elif l in self.word:
                status.append(LSTAT.PRESENT)
            else:
                status.append(LSTAT.MISSING)
        self.guesses.append(guess)
        self.statuses.append(status)

    def possible_words(self, words: list[str]) -> list[str]:
        ...


def random_word(words: Sequence[str] | None = None, seed: int | None = None) -> str:
    logger.debug("random seed", seed=seed)
    words = WORDS if words is None else words
    return random.choice(words)


def user_guess(words: Sequence[str] | None = None) -> str:
    words = WORDS if words is None else words
    while True:
        guess = input("Enter your guess (q to exit): ").strip().lower()
        logger.debug("user guess", guess=guess)
        if guess == "q":
            raise typer.Exit(1)
        if len(guess) != 5:
            print("Guess must be 5 letters long.")
            continue
        if guess not in words:
            print("Not in word list.")
            continue
        return guess


def main(seed: Optional[int] = None) -> None:
    """Py-Wordle."""
    logger.info("start game.")
    word = random_word(seed=seed)
    guesses = Guesses(word)
    logger.info("random word", word=word)
    for _ in range(6):
        guess = user_guess()
        guesses.add(guess)
        print(guesses)
        if guess == word:
            print("Well played.")
            return
    print(f"Unlucky. The word was {word}.")


if __name__ == "__main__":
    typer.run(main)
