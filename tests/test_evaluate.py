import pytest

from main import Status, evaluate, _score, _Status


@pytest.mark.parametrize(
    "aim,guess,expected",
    (
        ("troll", "twist", ("=", ".", ".", ".", ".")),
        ("scorn", "abeng", (".", ".", ".", "-", ".")),
        ("thump", "jetty", (".", ".", "-", ".", ".")),
    ),
)
def test_evaluate(aim: str, guess: str, expected: list[_Status]) -> None:
    got = evaluate(aim=aim, guess=guess)
    assert got == expected


@pytest.mark.parametrize(
    "status,expected",
    (
        ((".", ".", ".", ".", "."), 0),
        ((".", ".", "-", ".", "."), 1),
        ((".", ".", ".", ".", "-"), 1),
        ((".", "=", ".", ".", "."), 3),
        (("-", ".", ".", "=", "."), 4),
    ),
)
def test_score(status: Status, expected: int) -> None:
    got = _score(status)
    assert got == expected
