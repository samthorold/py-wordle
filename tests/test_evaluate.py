import pytest

from wordle.evaluate import evaluate, _score


@pytest.mark.parametrize(
    "aim,guess,expected",
    (
        ("troll", "twist", "=...."),
        ("scorn", "abeng", "...-."),
        ("thump", "jetty", "..-.."),
    ),
)
def test_evaluate(aim: str, guess: str, expected: str) -> None:
    got = evaluate(aim=aim, guess=guess)
    assert got == expected


@pytest.mark.parametrize(
    "status,expected",
    (
        (".....", 0),
        ("..-..", 1),
        ("....-", 1),
        (".=..-", 3),
        ("=====", 10),
    ),
)
def test_score(status: str, expected: int) -> None:
    got = _score(status)
    assert got == expected
