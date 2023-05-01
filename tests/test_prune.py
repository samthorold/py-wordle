import pytest

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
    words = WORDS
    guesses = [
        "motto",
    ]
    statuses = ["====="]
    expected = ["motto"]

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
    words = WORDS
    guesses = [
        guess,
    ]
    statuses = [status]

    got = prune(words=words, guesses=guesses, statuses=statuses)
    assert got == expected
