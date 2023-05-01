import functools
from wordle.models import GuessStatus, Status


SCORES = {
    Status.MISSING: 0,
    Status.PRESENT: 1,
    Status.CORRECT: 2,
}


@functools.cache
def present(aim: str, guess: str, guessc: str, i: int) -> Status:
    if i > 0:
        count_aimc = len([c for c in aim if c == guessc])
        count_stats = len([c for c in guess[:i] if c == guessc])
        if count_aimc <= count_stats:
            return Status.MISSING
    return Status.PRESENT


@functools.cache
def evaluate(aim: str, guess: str) -> GuessStatus:
    status = []
    for i, (aimc, guessc) in enumerate(zip(aim, guess)):
        if aimc == guessc:
            status.append(Status.CORRECT)
        elif guessc in aim:
            status.append(present(aim=aim, guess=guess, guessc=guessc, i=i))
        else:
            status.append(Status.MISSING)
    return GuessStatus(status)


@functools.cache
def _score(gs: tuple[Status]) -> int:
    return sum(SCORES[s] for s in gs)
