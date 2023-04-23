import pytest

from main import evaluate, LSTAT


@pytest.mark.parametrize(
    "aim,guess,expected",
    (
        (
            "troll",
            "twist",
            [
                LSTAT.CORRECT,
                LSTAT.MISSING,
                LSTAT.MISSING,
                LSTAT.MISSING,
                LSTAT.MISSING,
            ],
        ),
        (
            "scorn",
            "abeng",
            [
                LSTAT.MISSING,
                LSTAT.MISSING,
                LSTAT.MISSING,
                LSTAT.PRESENT,
                LSTAT.MISSING,
            ],
        ),
        (
            "thump",
            "jetty",
            [
                LSTAT.MISSING,
                LSTAT.MISSING,
                LSTAT.PRESENT,
                LSTAT.MISSING,
                LSTAT.MISSING,
            ],
        ),
    ),
)
def test_evaluate(aim: str, guess: str, expected: list[LSTAT]) -> None:
    got = evaluate(aim=aim, guess=guess)
    assert got == expected
