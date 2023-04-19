from enum import Enum
import random
from typing import Optional, Sequence

from rich import print
from rich.progress import track
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
        word: str | None = None,
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

    def add(self, guess: str, status: list[LSTAT] | None = None) -> None:
        status = [] if status is None else status
        if not status:
            if not self.word:
                raise ValueError(
                    "Must provide either a ground truth word or a guess status"
                )
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
        return word


def random_word(words: Sequence[str] | None = None, seed: int | None = None) -> str:
    # logger.debug("random seed", seed=seed)
    words = WORDS if words is None else words
    return random.choice(words)


def user_guess(words: Sequence[str] | None = None) -> str:
    words = WORDS if words is None else words
    while True:
        guess = typer.prompt("Enter your guess (q to exit)").strip().lower()
        if guess == "q":
            raise typer.Exit(1)
        if len(guess) != 5:
            print("Guess must be 5 letters long.")
            continue
        if guess not in words:
            print("Not in word list.")
            continue
        return guess


def user_status() -> list[LSTAT]:
    while True:
        status = typer.prompt("Guess results (.-=)").lower().strip()
        if len(status) != 5:
            print("Status must be 5 characters long.")
            continue
        try:
            lstats = [LSTAT(c) for c in status]
        except Exception:
            print("Could not parse status. Characters must be one on '.-='.")
        else:
            return lstats


def main(
    aim: Optional[str] = None,
    initial_guess: str = "crate",
    seed: Optional[int] = None,
    n: int = 1,
    show_guesses: bool = False,
    interactive: bool = False,
    progress: bool = True,
) -> None:
    """Py-Wordle."""
    if interactive:
        n = 1
        progress = False
        show_guesses = True
    words = WORDS
    results = []
    itr = range(n)
    if progress:
        itr = track(itr)
    for _ in itr:
        won = False
        word = random_word(words=words, seed=seed) if aim is None else aim
        guesser = Guesser(word, initial_guess=initial_guess)
        for _ in range(6):
            guess = guesser.guess()
            if show_guesses:
                print(guess)
            if interactive:
                status = user_status()
                if status == [LSTAT.CORRECT] * 5:
                    won = True
                    break
            else:
                status = None
            guesser.add(guess=guess, status=status)
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
    if n > 1:
        print(sum(results), len(results))


if __name__ == "__main__":
    typer.run(main)
