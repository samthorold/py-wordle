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
import argparse
import functools
import logging
import random
from typing import Iterator, Protocol, Self

from search.alphabeta import alphabeta


logger = logging.getLogger(__name__)


CORRECT_GUESS = "====="
COMPLETELY_WRONG = "....."
MINIMUM_NODE = "_____"
MAXIMUM_NODE = "^^^^^"


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
def score_evaluation(sc: str) -> int:
    logger.debug("score=%s", sc)
    if sc == MINIMUM_NODE:
        return -100
    if sc == MAXIMUM_NODE:
        return 100
    scores = {".": 0, "-": 1, "=": 2}
    return sum(scores[s] for s in sc)


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
    scores: list[str],
    final_only: bool = True,
) -> list[str]:
    if len(guesses) != len(scores):
        raise ValueError(
            "Pruning with different sizes guesses and scores not supported"
        )
    for guess, score in zip(reversed(guesses), reversed(scores)):
        if score == CORRECT_GUESS:
            return [guess]
        else:
            words = [w for w in words if w != guess]

        for i, (c, s) in enumerate(zip(guess, score)):
            match s:
                case "=":
                    words = prune_correct(words, i, c)
                case "-":
                    words = prune_present(words, i, c)
                case ".":
                    words = prune_missing(words, i, c, score, guess)
                case _:
                    raise ValueError(f"Unkown evaluation.")
        if final_only:
            break
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

    moves: list[str]

    def __init__(
        self,
        moves: list[str],
        vocabulary: list[str],
        depth: int = 1,
    ) -> None:
        self.moves = moves
        self.vocabulary = vocabulary
        self.depth = depth
        if vocabulary:
            logger.debug("create node %s %s %s", moves, depth, self.is_terminal())

    def __lt__(self, other: Self) -> bool:
        return self.score() < other.score()

    def __le__(self, other: Self) -> bool:
        return self.score() <= other.score()

    def __gt__(self, other: Self) -> bool:
        return self.score() > other.score()

    def __ge__(self, other: Self) -> bool:
        return self.score() >= other.score()

    def score(self) -> int:
        min_max_node = self.moves[-1] in [MINIMUM_NODE, MAXIMUM_NODE]
        if not self.is_maximising() or min_max_node:
            return score_evaluation(self.moves[-1])
        # And this is the crux
        # What is the score for a guess before knowing the
        # minimising player's turn
        # Returning the same score for all would _run_
        # but maybe only with soft alphabeta
        return 0

    def is_maximising(self) -> bool:
        return bool(self.depth % 2)

    def is_terminal(self) -> bool:
        no_more_guesses = self.depth == 13
        correct_guess = bool(self.moves) and self.moves[-1] == CORRECT_GUESS
        return no_more_guesses or correct_guess

    def children(self) -> Iterator[Self]:
        if self.is_maximising():
            self.prune()
            for guess in self.vocabulary:
                yield WordleNode(
                    moves=self.moves + [guess],
                    vocabulary=[w for w in self.vocabulary],
                    depth=self.depth + 1,
                )
        else:
            for guess in self.vocabulary:
                sc = evaluate(guess=self.moves[-1], aim=guess)
                logger.debug("%s %s", self.moves, sc)
                yield WordleNode(
                    moves=self.moves + [sc],
                    vocabulary=[w for w in self.vocabulary],
                    depth=self.depth + 1,
                )

    def prune(self) -> None:
        if len(self.moves) < 2:
            return
        self.vocabulary = prune(
            words=self.vocabulary,
            guesses=self.moves[-2:-1],
            scores=self.moves[-1:],
            final_only=True,
        )

    def maximum(self) -> WordleNode:
        return WordleNode(vocabulary=[], moves=[MAXIMUM_NODE])

    def minimum(self) -> WordleNode:
        return WordleNode(vocabulary=[], moves=[MINIMUM_NODE])


class AlphaBetaGuesser:
    def __init__(self, vocabulary: list[str]) -> None:
        self.vocabulary = vocabulary

    def __call__(self, guesses: list[str], scores: list[str]) -> str:
        if not guesses:
            return "crate"
        if len(guesses) == 1 and scores[-1] == COMPLETELY_WRONG:
            return "bogus"
        vocabulary = prune(
            words=self.vocabulary,
            guesses=guesses,
            scores=scores,
            final_only=False,
        )
        node = WordleNode(
            moves=[guesses[-1], scores[-1]],
            vocabulary=vocabulary,
            depth=1 + len(guesses) * 2,
        )
        best_guess = alphabeta(
            node,
            a=node.minimum(),
            b=node.maximum(),
            soft=True,
        )
        logger.info("best node move=%s moves=%s", best_guess.moves[-2], best_guess.moves)
        return best_guess.moves[-2]


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
        logger.info("move %s %s", self.guesses, self.scores)
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
    guesser: Guesser,
) -> None:
    wordle = Wordle(
        guesser=guesser,
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


class WordleArgs:
    def __init__(
        self,
        truth: str,
        vocabulary: list[str],
        guesser: Guesser,
        log_level: str,
    ) -> None:
        if truth not in vocabulary:
            raise ValueError(f"Target '{truth}' not in vocabulary.")
        self.truth = truth
        self.vocabulary = vocabulary
        self.guesser = guesser
        self.log_level = log_level.upper()

    @classmethod
    def from_argument_parser(cls, cli: argparse.ArgumentParser) -> WordleArgs:
        args = cli.parse_args()
        vocab_path = (
            "words/words.txt" if args.vocabulary is None else args.vocabulary
        )
        with open(vocab_path) as f:
            vocabulary = [line.strip().lower() for line in f]
        truth = random.choice(vocabulary) if args.truth is None else args.truth
        guesser = (
            UserGuesser(vocabulary=vocabulary)
            if args.interactive
            else AlphaBetaGuesser(vocabulary)
        )
        return WordleArgs(
            truth=truth,
            vocabulary=vocabulary,
            guesser=guesser,
            log_level=args.log_level,
        )


cli = argparse.ArgumentParser()
cli.add_argument("--truth")
cli.add_argument("--vocabulary")
cli.add_argument("--log-level", default="WARNING")
cli.add_argument("--interactive", action="store_true")

if __name__ == "__main__":
    print("=== PyWordle ===")
    args = WordleArgs.from_argument_parser(cli)
    logging.basicConfig(level=args.log_level)
    main(truth=args.truth, vocabulary=args.vocabulary, guesser=args.guesser)
    print(args.truth)
