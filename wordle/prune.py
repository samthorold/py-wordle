from wordle.models import CORRECT_GUESS, Guess, GuessStatus, Status


def prune(
    words: set[str],
    guesses: list[Guess],
    statuses: list[GuessStatus],
) -> set[str]:
    for guess, status in zip(guesses, statuses):
        guess_str = guess.guess
        if status == CORRECT_GUESS:
            return set([str(guess)])
        else:
            words = set([w for w in words if w != guess_str])

        for i, (c, s) in enumerate(zip(guess_str, status)):
            match s:
                case Status.CORRECT:
                    words = set([w for w in words if w[i] == c])
                case Status.PRESENT:
                    words = set([w for w in words if c in w and w[i] != c])
                case Status.MISSING:
                    # But, I use missing when there are present characters
                    # but too many of them
                    # So, if the letter is present or correct anywhere
                    # elsewhere skip this missing filter
                    stats = [s for s, c_ in zip(status, guess_str) if c_ == c]
                    if any(s != Status.MISSING for s in stats):
                        words = set([w for w in words if c in w and w[i] != c])
                        continue
                    words = set([w for w in words if c not in w])
    return words
