import pytest

from main import evaluate, score, CharStat


@pytest.mark.parametrize(
    "aim,guess,expected",
    (
        (
            "troll",
            "twist",
            [
                CharStat.CORRECT,
                CharStat.MISSING,
                CharStat.MISSING,
                CharStat.MISSING,
                CharStat.MISSING,
            ],
        ),
        (
            "scorn",
            "abeng",
            [
                CharStat.MISSING,
                CharStat.MISSING,
                CharStat.MISSING,
                CharStat.PRESENT,
                CharStat.MISSING,
            ],
        ),
        (
            "thump",
            "jetty",
            [
                CharStat.MISSING,
                CharStat.MISSING,
                CharStat.PRESENT,
                CharStat.MISSING,
                CharStat.MISSING,
            ],
        ),
    ),
)
def test_evaluate(aim: str, guess: str, expected: list[CharStat]) -> None:
    got = evaluate(aim=aim, guess=guess)
    assert got == expected


@pytest.mark.parametrize(
    "status,expected",
    (
        (".....", 0),
        ("-....", 1),
        ("....-", 1),
        ("....=", 3),
        (".-..=", 4),
    ),
)
def test_score(status: str, expected: int) -> None:
    st = CharStat.from_string(status)
    got = score(st)
    assert got == expected
