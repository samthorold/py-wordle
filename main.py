from collections import Counter
from enum import Enum
import random
from typing import Optional, Sequence

from rich import print
from rich.progress import track
import structlog
import typer


logger = structlog.get_logger()


NUMBER_OF_GUESSES = 13


class LSTAT(Enum):
    MISSING = "."
    PRESENT = "-"
    CORRECT = "="
    UNKNOWN = " "


def evaluate(aim: str, guess: str) -> list[LSTAT]:
    result: list[tuple[str, LSTAT]] = []
    for i, (aimc, guessc) in enumerate(zip(aim, guess)):
        if aimc == guessc:
            result.append((guessc, LSTAT.CORRECT))
        elif guessc in aim:
            if i > 0:
                # breakpoint()
                count_aimc = len([c for c in aim if c == guessc])
                count_stats = len([c for c, _ in result if c == guessc])
                if count_aimc <= count_stats:
                    result.append((guessc, LSTAT.MISSING))
                    continue
            result.append((guessc, LSTAT.PRESENT))
        else:
            result.append((guessc, LSTAT.MISSING))
    return [stat for _, stat in result]


class Guesser:
    def __init__(
        self,
        words: list[str],
        guesses: list[str] | None = None,
        statuses: list[list[LSTAT]] | None = None,
        initial_guess: str | None = None,
    ):
        self.words = words
        self.guesses = [] if guesses is None else guesses
        self.statuses = [] if statuses is None else statuses
        self.initial_guess = initial_guess

    def __len__(self) -> int:
        return len(self.guesses)

    def __str__(self) -> str:
        return "\n".join(
            ["".join(f"{s.value}" for s in status) for status in self.statuses]
        )

    def add(self, guess: str, status: list[LSTAT]) -> None:
        self.guesses.append(guess)
        self.statuses.append(status)

    def update_words(self) -> None:
        if self.guesses:
            prev_g = self.guesses[-1]
            for i, (s, c) in enumerate(zip(self.statuses[-1], prev_g)):
                match s:
                    case LSTAT.CORRECT:
                        self.words = [
                            w for w in self.words if w[i] == c and w != prev_g
                        ]
                    case LSTAT.PRESENT:
                        self.words = [
                            w
                            for w in self.words
                            if c in w and w[i] != c and w != prev_g
                        ]
                    case LSTAT.MISSING:
                        # But, I use missing when there are present characters
                        # but too many of them
                        # So, if the letter is present or correct anywhere
                        # elsewhere skip this missing filter
                        stats = [
                            s
                            for s, c_ in zip(self.statuses[-1], prev_g)
                            if c_ == c
                        ]
                        # breakpoint()
                        if any(s != LSTAT.MISSING for s in stats):
                            self.words = [
                                w
                                for w in self.words
                                if c in w and w[i] != c and w != prev_g
                            ]
                            continue
                        self.words = [
                            w for w in self.words if c not in w and w != prev_g
                        ]

        self.rank_words()

    def rank_words(self) -> None:
        rank = [(-len(set(word)), word) for word in self.words]
        # breakpoint()
        self.words = [word for _, word in sorted(rank)]

    def guess(self) -> str:
        if self.initial_guess:
            word = self.initial_guess
        else:
            self.update_words()
            word = self.words[0]
        return word


def random_word(words: Sequence[str], seed: int | None = None) -> str:
    return random.choice(words)


def user_guess(words: Sequence[str]) -> str:
    while True:
        guess: str = (
            typer.prompt("Enter your guess (q to exit)").strip().lower()
        )
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


def game(
    guesser: Guesser,
    show_guesses: bool,
    interactive: bool,
    aim: str = "xxxxx",
) -> tuple[int, str, str, list[str]]:
    for guess_number in range(1, NUMBER_OF_GUESSES + 1):
        guess = guesser.guess()
        if show_guesses:
            print(guess)
        if interactive:
            status = user_status()
        else:
            status = evaluate(aim=aim, guess=guess)
        guesser.add(guess=guess, status=status)
        if status == [LSTAT.CORRECT] * 5:
            return guess_number, aim, guesser.guesses[-1], guesser.words
    return 0, aim, guesser.guesses[-1], guesser.words


def main(
    aim: Optional[str] = None,
    initial_guess: Optional[str] = None,
    seed: Optional[int] = None,
    n: int = 1,
    show_guesses: bool = False,
    interactive: bool = False,
    progress: bool = True,
    all_words: bool = False,
) -> None:
    """Py-Wordle."""

    if interactive or aim:
        n = 1
        progress = False
        show_guesses = True

    with open("words.txt") as fh:
        words = fh.read().splitlines()

    if all_words:
        n = len(words)

    results = []
    for i in track(range(n)) if progress else range(n):
        if all_words:
            aim = words[i]
        if interactive and aim is None:
            aim = "xxxxx"
        guesser = Guesser(words=words, initial_guess=initial_guess)
        result, aim_, last, poss = game(
            guesser=guesser,
            show_guesses=show_guesses,
            interactive=interactive,
            aim=aim or random_word(words=words, seed=seed),
        )
        results.append(result)
        if result == 0:
            if aim_ not in poss:
                raise ValueError("Aim not in possibilities.")
            print(f"Unlucky. {aim_} ({last}) {poss}")
        if show_guesses:
            if result == 0:
                print("Unlucky.")
            else:
                print("Congratulations.")
    if n > 1:
        correct = len([i for i in results if i > 0])
        cts = Counter(results)
        for i in range(0, NUMBER_OF_GUESSES + 1):
            print(f"{i}:{cts[i]:>6}")
        print(correct, len(results), round(correct / len(results) * 100))


if __name__ == "__main__":
    typer.run(main)
