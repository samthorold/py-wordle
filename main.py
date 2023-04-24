from __future__ import annotations
import functools
import sys
from typing import Literal


_Status = Literal[".", "-", "="]

Status = tuple[_Status, _Status, _Status, _Status, _Status]

SCORES: dict[_Status, int] = {"=": 3, "-": 1, ".": 0}

ALL_MISSING: Status = tuple([".", ".", ".", ".", "."])

MAX_TURNS = 6


def present(aim: str, guess: str, guessc: str, i: int) -> _Status:
    if i > 0:
        count_aimc = len([c for c in aim if c == guessc])
        count_stats = len([c for c in guess[:i] if c == guessc])
        if count_aimc <= count_stats:
            return "."
    return "-"


@functools.cache
def evaluate(aim: str, guess: str) -> Status:
    stats: list[_Status] = []
    for i, (aimc, guessc) in enumerate(zip(aim, guess)):
        if aimc == guessc:
            stats.append("=")
        elif guessc in aim:
            stats.append(present(aim=aim, guess=guess, guessc=guessc, i=i))
        else:
            stats.append(".")
    return tuple([stats[0], stats[1], stats[2], stats[3], stats[4]])


def _score(status: Status, scores: dict[_Status, int] | None = None) -> int:
    scores = SCORES if scores is None else scores
    return sum(scores.get(s, 0) for s in status)


def calculate_score(
    word: str, aim: str, scores: dict[_Status, int] | None = None
) -> tuple[int, Status]:
    status = evaluate(aim=aim, guess=word)
    return _score(status, scores=scores), status


def prune(words: list[str], guess: str, status: Status) -> list[str]:
    for i, (s, c) in enumerate(zip(status, guess)):
        match s:
            case "=":
                words = [w for w in words if w[i] == c and w != guess]
            case "-":
                words = [
                    w for w in words if c in w and w[i] != c and w != guess
                ]
            case ".":
                # f the letter is present or correct anywhere
                # elsewhere skip this missing filter
                stats = [s for s, c_ in zip(status, guess) if c_ == c]
                if any(s != "." for s in stats):
                    words = [
                        w for w in words if c in w and w[i] != c and w != guess
                    ]
                    continue
                words = [w for w in words if c not in w and w != guess]
    return words


def worst_case(
    guess: str,
    words: list[str],
    scores: dict[_Status, int] | None = None,
) -> Status:
    min_score = 6
    min_status = ALL_MISSING
    if not words:
        raise ValueError("No words remaining.")
    for aim in words:
        score, status = calculate_score(word=guess, aim=aim, scores=scores)
        if score <= min_score:
            min_score = score
            min_status = status
    return min_status


class Node:
    def __init__(self, last_status: Status, last_guess: str, words: list[str]):
        self.last_status = last_status
        self.last_guess = last_guess
        self.words = words


def maximin(node: Node, depth: int, turn: bool = True) -> int:
    if turn:
        if depth == 6:
            words = prune(words=node.words, guess=node.last_guess, status=node.last_status)
            value = -1
            for word in words:
                value = min(value, _score(worst_case(guess=word, words=words)))
            return value

    



def maximin(
    word: str,
    words: list[str],
    depth: int,
) -> tuple[int, str, Status]:
    if not words:
        return 0, prune_guess, prune_status

    pfx = "  " * depth
    min_score = 6
    min_word = "xxxxx"
    min_status = ALL_MISSING

    worst: dict[str, int] = {}

    for guess in words:
        status = worst_case(guess, words=words)
        score = _score(status)
        worst[guess] = score

        if score <= min_score:
            min_score = score
            min_word = guess
            min_status = status

    print(f"{pfx} {depth} {min_score=} {min_word=} {min_status=}")

    if depth == 6:
        return min_score, min_word, min_status

    max_score = -100
    max_word = "xxxxx"
    max_status = ALL_MISSING
    for word in words:
        if worst
        word_score, _, word_status = maximin(
            words=words,
            depth=depth + 1,
            prune_guess=min_word,
            prune_status=min_status,
        )
        score = max(
            word_score,
            _score(worst_case(guess=word, words=words)),
        )
        if score >= max_score:
            max_score = score
            max_word = word
            max_status = word_status
    print(f"{pfx} {depth} {max_score=} {max_word=} {max_status=}")
    return max_score, max_word, max_status


def game(aim: str, words: list[str]) -> None:
    last_guess = "xxxxx"
    last_status = ALL_MISSING
    for i in range(1, 7):
        print(f"{i}: [{len(words)}] guess ...")
        if i == 1:
            guess = "crate"
        else:
            _, guess, _ = maximin(
                words, depth=i, prune_guess=last_guess, prune_status=last_status
            )
        status = evaluate(guess=guess, aim=aim)
        last_guess = guess
        last_status = status
        print(f"  {guess} {status} ")
        if guess == aim:
            break
        # print("  pruning ...")
        # words = prune(words, guess, status)
    print(aim)


def main() -> int:
    words_file = "words-min.txt"
    with open(words_file) as fh:
        words = fh.read().splitlines()

    game("masse", words)
    return 0


if __name__ == "__main__":
    code = main()
    sys.exit(code)
