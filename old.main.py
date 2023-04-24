from __future__ import annotations
from collections import Counter
from enum import Enum
import functools
from pathlib import Path
import random
from typing import Optional, Sequence

from rich import print
from rich.progress import track
import typer


class CharStat(Enum):
    MISSING = "."
    PRESENT = "-"
    CORRECT = "="
    UNKNOWN = " "

    @classmethod
    def from_string(cls, string: str) -> Status:
        return (
            cls(string[0]),
            cls(string[1]),
            cls(string[2]),
            cls(string[3]),
            cls(string[4]),
        )


SCORES = {
    "-": 1,
    "=": 3,
}


Status = tuple[CharStat, CharStat, CharStat, CharStat, CharStat]


def score(status: Status, scores: dict[CharStat, int] | None = None) -> int:
    scores = SCORES if scores is None else scores
    return sum(scores.get(s, 0) for s in status)


def present(aim: str, guess: str, guessc: str, i: int) -> CharStat:
    if i > 0:
        count_aimc = len([c for c in aim if c == guessc])
        count_stats = len([c for c in guess[:i] if c == guessc])
        if count_aimc <= count_stats:
            return "."
    return "-"


@functools.cache
def evaluate(aim: str, guess: str) -> Status:
    stats: list[CharStat] = []
    for i, (aimc, guessc) in enumerate(zip(aim, guess)):
        if aimc == guessc:
            stats.append("=")
        elif guessc in aim:
            stats.append(present(aim=aim, guess=guess, guessc=guessc, i=i))
        else:
            stats.append(".")
    return tuple([stats[0], stats[1], stats[2], stats[3], stats[4]])


def score_word(
    word: str, aim: str, scores: dict[CharStat, int] | None = None
) -> int:
    status = evaluate(aim=aim, guess=word)
    return score(status, scores=scores)


class Guesser:
    def __init__(
        self,
        words: list[str],
        number_of_guesses: int,
        tree_under: int,
        guesses: list[str] | None = None,
        statuses: list[Status] | None = None,
        initial_guess: str | None = None,
        ranked: bool = False,
    ):
        self.words = words
        self.number_of_guesses = number_of_guesses
        self.tree_under = tree_under
        self.guesses = [] if guesses is None else guesses
        self.statuses = [] if statuses is None else statuses
        self.initial_guess = initial_guess
        self.ranked = ranked

    def __len__(self) -> int:
        return len(self.guesses)

    def __str__(self) -> str:
        return "\n".join(
            ["".join(f"{s.value}" for s in status) for status in self.statuses]
        )

    def copy(self) -> Guesser:
        return Guesser(
            words=self.words,
            number_of_guesses=self.number_of_guesses,
            tree_under=self.tree_under,
            guesses=self.guesses,
            statuses=self.statuses,
            ranked=self.ranked,
        )

    def add(self, guess: str, status: Status) -> None:
        self.guesses.append(guess)
        self.statuses.append(status)

    def update_words(self) -> None:
        if self.guesses:
            prev_g = self.guesses[-1]
            for i, (s, c) in enumerate(zip(self.statuses[-1], prev_g)):
                match s:
                    case "=":
                        self.words = [
                            w for w in self.words if w[i] == c and w != prev_g
                        ]
                    case "-":
                        self.words = [
                            w
                            for w in self.words
                            if c in w and w[i] != c and w != prev_g
                        ]
                    case ".":
                        # But, I use missing when there are present characters
                        # but too many of them
                        # So, if the letter is present or correct anywhere
                        # elsewhere skip this missing filter
                        stats = [
                            s
                            for s, c_ in zip(self.statuses[-1], prev_g)
                            if c_ == c
                        ]
                        if any(s != "." for s in stats):
                            self.words = [
                                w
                                for w in self.words
                                if c in w and w[i] != c and w != prev_g
                            ]
                            continue
                        self.words = [
                            w for w in self.words if c not in w and w != prev_g
                        ]

    def rank_words(self) -> None:
        if self.ranked:
            return
        letters = "".join(self.words)
        ctr = Counter(letters)
        letter_ranks = dict(zip(ctr, range(len(ctr), 0, -1)))
        rank = [
            (-len(set(word)) * 5 - sum(letter_ranks[c] for c in word), word)
            for word in self.words
        ]
        self.words = [word for _, word in sorted(rank)]
        self.ranked = True

    def most_wins(self) -> str:
        results = []
        self.rank_words()
        # i = 0
        for maybe in self.words:
            # break_maybe = False
            word_results = []
            for aim in self.words:
                # if i > 1_000_000_000:
                #     break_maybe = True
                #     break
                guesser = self.copy()
                guesser.initial_guess = maybe
                self.initial_guess = maybe
                result, *_ = game(
                    guesser=guesser,
                    show_guesses=False,
                    interactive=False,
                    number_of_guesses=self.number_of_guesses - 1,
                    aim=aim,
                    start_guess=len(self.guesses),
                )
                self.initial_guess = None
                word_results.append(result)
                # i += 1
            results.append((-sum([r or 7 for r in word_results]), maybe))
            # if break_maybe:
            #     break
        results = sorted(results)
        return results[0][1]

    def guess(self) -> str:
        if self.initial_guess is not None:
            word = self.initial_guess
            self.initial_guess = None
        else:
            self.update_words()
            word = self.most_wins()
        self.number_of_guesses -= 1
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


def user_status() -> Status:
    while True:
        status = typer.prompt("Guess results (.-=)").lower().strip()
        if len(status) != 5:
            print("Status must be 5 characters long.")
            continue
        try:
            lstats = [CharStat(c) for c in status]
        except Exception:
            print("Could not parse status. Characters must be one on '.-='.")
        else:
            return tuple(
                [lstats[0], lstats[1], lstats[2], lstats[3], lstats[4]]
            )


def game(
    guesser: Guesser,
    show_guesses: bool,
    interactive: bool,
    number_of_guesses: int,
    aim: str = "xxxxx",
    start_guess: int = 1,
) -> tuple[int, str, str, str, list[str]]:
    guess = "xxxxx"
    for guess_number in range(start_guess, number_of_guesses + 1):
        if show_guesses:
            print(f"Remaining words: {len(guesser.words)}")
        guess = guesser.guess()
        if show_guesses:
            print(f"{guess_number}: {guess}")
        if interactive:
            status = user_status()
        else:
            status = evaluate(aim=aim, guess=guess)
        guesser.add(guess=guess, status=status)
        if status == ["="] * 5:
            return guess_number, guess, aim, guesser.guesses[-1], guesser.words
    return 0, guess, aim, guesser.guesses[-1], guesser.words


def main(
    aim: Optional[str] = None,
    initial_guess: Optional[str] = None,
    seed: Optional[int] = None,
    n: int = 1,
    number_of_guesses: int = 6,
    tree_under: int = 20,
    show_guesses: bool = False,
    interactive: bool = False,
    progress: bool = True,
    all_words: bool = False,
    words_file: Path = Path("words.txt"),
) -> None:
    """Py-Wordle."""

    if interactive or aim or n == 1:
        n = 1
        progress = False
        show_guesses = True

    with open(words_file) as fh:
        words = fh.read().splitlines()
        random.shuffle(words)

    if all_words:
        n = len(words)
        progress = True
        show_guesses = False

    results = []
    for i in track(range(n)) if progress else range(n):
        if all_words:
            aim = words[i]
        if interactive and aim is None:
            aim = "xxxxx"
        guesser = Guesser(
            words=words,
            number_of_guesses=number_of_guesses,
            tree_under=tree_under,
            initial_guess=initial_guess,
        )
        result, _, aim_, last, poss = game(
            guesser=guesser,
            show_guesses=show_guesses,
            interactive=interactive,
            number_of_guesses=number_of_guesses,
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
        for i in range(0, number_of_guesses + 1):
            print(f"{i}:{cts[i]:>6}")
        print(correct, len(results), round(correct / len(results) * 100))


if __name__ == "__main__":
    typer.run(main)
