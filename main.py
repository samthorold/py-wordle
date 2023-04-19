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


class Guesser:
    def __init__(
        self,
        word: str,
        guesses: list[str] | None = None,
        statuses: list[list[LSTAT]] | None = None,
        words: list[str] | None = None,
        initial_guess: str = "crate",
    ):
        self.word = word
        self.guesses = [] if guesses is None else guesses
        self.statuses = [] if statuses is None else statuses
        self.words = WORDS if words is None else words
        self.initial_guess = initial_guess

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

    def update_words(self) -> None:
        # breakpoint()
        if not self.guesses:
            return
        # if the game is still going the last guess was incorrect
        self.words = [w for w in self.words if w != self.guesses[-1]]
        for i, (s, c) in enumerate(zip(self.statuses[-1], self.guesses[-1])):
            match s:
                case LSTAT.CORRECT:
                    self.words = [w for w in self.words if w[i] == c]
                case LSTAT.PRESENT:
                    self.words = [w for w in self.words if c in w]
                case LSTAT.MISSING:
                    self.words = [w for w in self.words if c not in w]

    def guess(self) -> str:
        if not self.guesses:
            word = self.initial_guess
        else:
            self.update_words()
            word = self.words[0]
        # logger.info("guess", guess=word)
        self.add(word)
        return word


def random_word(words: Sequence[str] | None = None, seed: int | None = None) -> str:
    # logger.debug("random seed", seed=seed)
    words = WORDS if words is None else words
    return random.choice(words)


def main(
    aim: Optional[str] = None,
    initial_guess: str = "crate",
    seed: Optional[int] = None,
    n: int = 1,
    show_guesses: bool = False,
) -> None:
    """Py-Wordle."""
    # logger.info("start game.")
    words = WORDS
    results = []
    for i in range(n):
        won = False
        word = random_word(words=words, seed=seed) if aim is None else aim
        # logger.info("aim", aim=word)
        guesser = Guesser(word, initial_guess=initial_guess)
        for _ in range(6):
            guess = guesser.guess()
            if show_guesses:
                print(guess)
                # print(guesser)
            if guess == word:
                if n == 1:
                    print(f"Well played. The word was {word}")
                won = True
                results.append(1)
                break
        if not won:
            if n == 1:
                print(f"Unlucky. The word was {word}.")
            results.append(0)
    print(sum(results), len(results))


if __name__ == "__main__":
    typer.run(main)
