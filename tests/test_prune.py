import pytest

from wordle.models import Guess, GuessStatus
from wordle.prune import prune


WORDS = [
    "abbot",
    "scorn",
    "today",
    "rider",
    "dizzy",
    "crime",
    "rakes",
    "clear",
    "leech",
    "burnt",
    "monic",
    "motto",
    "noose",
    "maxim",
    "crate",
]


def test_prune_correct_guess() -> None:
    words = set(WORDS)
    guesses = [
        Guess("motto"),
    ]
    statuses = [GuessStatus.from_string("=====")]
    expected = set(["motto"])

    got = prune(words=words, guesses=guesses, statuses=statuses)
    assert got == expected


@pytest.mark.parametrize(
    "guess,status,expected",
    (
        ("motto", ".--..", ["abbot"]),
        ("motto", ".=-..", ["today"]),
    ),
)
def test_prune_single(guess: str, status: str, expected: list[str]) -> None:
    words = set(WORDS)
    guesses = [
        Guess(guess),
    ]
    statuses = [GuessStatus.from_string(status)]

    got = prune(words=words, guesses=guesses, statuses=statuses)
    assert got == set(expected)
