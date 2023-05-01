import pytest

from wordle import GuessStatus, evaluate, _score


@pytest.mark.parametrize(
    "aim,guess,expected",
    (
        ("troll", "twist", GuessStatus.from_string("=....")),
        ("scorn", "abeng", GuessStatus.from_string("...-.")),
        ("thump", "jetty", GuessStatus.from_string("..-..")),
    ),
)
def test_evaluate(aim: str, guess: str, expected: GuessStatus) -> None:
    got = evaluate(aim=aim, guess=guess)
    assert got == expected


@pytest.mark.parametrize(
    "status,expected",
    (
        (GuessStatus.from_string("....."), 0),
        (GuessStatus.from_string("..-.."), 1),
        (GuessStatus.from_string("....-"), 1),
        (GuessStatus.from_string(".=..-"), 3),
        (GuessStatus.from_string("====="), 10),
    ),
)
def test_score(status: GuessStatus, expected: int) -> None:
    got = _score(tuple(status.status))
    assert got == expected
