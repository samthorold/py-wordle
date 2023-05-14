import functools


SCORES = {
    ".": 0,
    "-": 1,
    "=": 6,
}


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
def _score(gs: str) -> int:
    return sum(SCORES[s] for s in gs)
