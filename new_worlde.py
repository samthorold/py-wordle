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
import os
import random
from typing import Protocol

import functools


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
        correct_guess = any(s == "=====" for s in self.scores)
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
