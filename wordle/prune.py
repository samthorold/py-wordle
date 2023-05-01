CORRECT_GUESS = "====="

def prune_correct(words: list[str], i: int, c: str) -> list[str]:
    return [w for w in words if w[i] == c]


def prune_present(words: list[str], i: int, c: str) -> list[str]:
    return [w for w in words if c in w and w[i] != c]


def prune_missing(
    words: list[str], i: int, c: str, status: str, guess: str
) -> list[str]:
    # Character with missing may be present elsewhere in the word
    # return [w for w in words if w[i] != c]
    if [s for s, c_ in zip(status, guess) if c_ == c and s != "."]:
        return [w for w in words if c in w and w[i] != c]
    return [w for w in words if c not in w]


def prune(
    words: list[str],
    guesses: list[str],
    statuses: list[str],
) -> list[str]:
    for guess, status in zip(guesses, statuses):
        if status == CORRECT_GUESS:
            return [guess]
        else:
            words = [w for w in words if w != guess]

        for i, (c, s) in enumerate(zip(guess, status)):
            match s:
                case "=":
                    words = prune_correct(words, i, c)
                case "-":
                    words = prune_present(words, i, c)
                case ".":
                    words = prune_missing(words, i, c, status, guess)
    return words
