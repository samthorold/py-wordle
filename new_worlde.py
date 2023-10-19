"""
>>> wdl = Wordle("rasps")
>>> wdl.guess("crate")
>>> wdl.score()
'.--..'
>>> wdl.guess("rates")
>>> wdl.score()
'==..='
>>> wdl.guess("rasps")
>>> wdl.score()
'====='
>>> wdl.is_terminal()
True
"""
from __future__ import annotations
import functools
import os
import random
from typing import Iterable, Protocol, Self

from search.alphabeta import alphabeta


@functools.cache
def present(aim: str, guess: str, guessc: str, i: int) -> str:
    if i > 0:
        count_aimc = len([c for c in aim if c == guessc])
        count_stats = len([c for c in guess[:i] if c == guessc])
        if count_aimc <= count_stats:
            return "."
    return "-"


@functools.cache
def evaluate(aim: str, guess: str) -> str:
    status = ""
    for i, (aimc, guessc) in enumerate(zip(aim, guess)):
        if aimc == guessc:
            status += "="
        elif guessc in aim:
            status += present(aim=aim, guess=guess, guessc=guessc, i=i)
        else:
            status += "."
    return status


@functools.cache
def score(sc: str) -> int:
    scores = {".": 0, "-": 1, "=": 2}
    return sum(scores[s] for s in sc)


CORRECT_GUESS = "====="


def prune_correct(words: list[str], i: int, c: str) -> list[str]:
    return [w for w in words if w[i] == c]


def prune_present(words: list[str], i: int, c: str) -> list[str]:
    return [w for w in words if c in w and w[i] != c]


def prune_missing(
    words: list[str], i: int, c: str, status: str, guess: str
) -> list[str]:
    # Character with missing may be present elsewhere in the word
    # return [w for w in words if w[i] != c]
    if [s for s, c_ in zip(status, guess) if c_ == c and s != "."]:
        return [w for w in words if c in w and w[i] != c]
    return [w for w in words if c not in w]


def prune(
    words: list[str],
    guesses: list[str],
    statuses: list[str],
) -> list[str]:
    for guess, status in zip(guesses, statuses):
        if status == CORRECT_GUESS:
            return [guess]
        else:
            words = [w for w in words if w != guess]

        for i, (c, s) in enumerate(zip(guess, status)):
            match s:
                case "=":
                    words = prune_correct(words, i, c)
                case "-":
                    words = prune_present(words, i, c)
                case ".":
                    words = prune_missing(words, i, c, status, guess)
                case _:
                    raise ValueError(f"Unkown evaluation.")
    return words


class Guesser(Protocol):
    def __call__(self, guesses: list[str], scores: list[str]) -> str:
        ...


class Scorer:
    def __init__(self, truth: str) -> None:
        self.truth = truth

    def __call__(self, guess: str) -> str:
        return evaluate(self.truth, guess)


class UserGuesser:
    def __init__(self, vocabulary: list[str]) -> None:
        self.vocabulary = vocabulary

    def __call__(self, guesses: list[str], scores: list[str]) -> str:
        while True:
            guess = input("Guess: ").strip().lower()
            if len(guess) != 5:
                print("Guess must be 5 letters long. Enter another.")
                continue
            if not guess in self.vocabulary:
                print("Guess not a known word.")
                continue
            return guess


class WordleNode:
    """Node in a Wordle game.

    The maximising player chooses the highest scoring allowed word.
    The minimising player chooses the lowest score that guess could have attained,
    given the allowed words.

    """

    def __init__(
        self,
        guess: str,
        score: str,
        vocabulary: list[str],
        depth: int = 1,
    ) -> None:
        self._guess = guess
        self._score = score
        self.vocabulary = vocabulary
        self.depth = depth

    def __lt__(self, other: Self) -> bool:
        return self.score() < other.score()

    def __le__(self, other: Self) -> bool:
        return self.score() <= other.score()

    def __gt__(self, other: Self) -> bool:
        return self.score() > other.score()

    def __ge__(self, other: Self) -> bool:
        return self.score() >= other.score()

    def score(self) -> int:
        if self.is_maximising():
            # And this is the crux
            # What is the score for a guess before knowing the
            # minimising player's turn
            return 0
        return score(self._score)

    def is_maximising(self) -> bool:
        return bool(self.depth % 2)

    def is_terminal(self) -> bool:
        return self.depth == 12

    def children(self) -> Iterable[Self]:
        if self.is_maximising():
            # Must know the actual score for the last guess
            # Can prune the allowed word list
            self.prune()
            for guess in self.vocabulary:
                yield WordleNode(
                    guess=guess,
                    score="",
                    vocabulary=[w for w in self.vocabulary],
                    depth=self.depth + 1,
                )
        else:
            for guess in self.vocabulary:
                yield WordleNode(
                    guess=self._guess,
                    score=evaluate(guess=self._guess, aim=guess),
                    vocabulary=[w for w in vocabulary],
                    depth=self.depth + 1,
                )

    def prune(self) -> None:
        ...


class AlphaBetaGuesser:
    ...


class Wordle:
    def __init__(
        self,
        guesser: Guesser,
        scorer: Scorer,
        vocabulary: list[str],
    ) -> None:
        self.guesser = guesser
        self.scorer = scorer
        self.vocabulary = vocabulary
        self.guess_next = True
        self.guesses: list[str] = []
        self.scores: list[str] = []

    def __str__(self) -> str:
        string = "\n".join(
            f"{guess} {score}" for guess, score in zip(self.guesses, self.scores)
        )
        if len(self.guesses) > len(self.scores):
            string += f"\n{self.guesses[-1]}"
        return string

    def guess(self, guess: str) -> None:
        if len(self.guesses) > len(self.scores):
            raise RuntimeError("Score the last guess first.")
        self.guesses.append(guess)

    def score(self) -> str:
        if len(self.scores) == len(self.guesses):
            raise RuntimeError("Make another guess first.")
        score = self.scorer(self.guesses[-1])
        self.scores.append(score)
        return score

    def move(self) -> None:
        if self.guess_next:
            self.guess(self.guesser(guesses=self.guesses, scores=self.scores))
        else:
            self.score()
        self.guess_next = not self.guess_next

    def is_terminal(self) -> bool:
        correct_guess = any(s == CORRECT_GUESS for s in self.scores)
        no_more_guesses = len(self.scores) == 6
        return correct_guess or no_more_guesses


def main(
    truth: str,
    vocabulary: list[str],
) -> None:
    wordle = Wordle(
        guesser=UserGuesser(vocabulary=vocabulary),
        scorer=Scorer(truth=truth),
        vocabulary=vocabulary,
    )
    while True:
        wordle.move()
        if len(wordle.scores) == len(wordle.guesses):
            print(wordle)
        print("---")
        if wordle.is_terminal():
            break


if __name__ == "__main__":
    print("=== PyWordle ===")
    vocab_path = os.environ.get("WORDLE_VOCAB_PATH", "words/words.txt")
    with open(vocab_path) as f:
        vocabulary = [line.strip().lower() for line in f]
    truth = random.choice(vocabulary)
    main(truth=truth, vocabulary=vocabulary)
    print(truth)
