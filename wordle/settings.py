import os


NUM_GUESSES = 6
GUESS_LEN = 5


class Settings:
    def __init__(
        self,
        num_guesses: int | None = None,
        guess_len: int | None = None,
    ):
        if num_guesses is None:
            num_guesses = int(os.environ.get("WORDLE_NUM_GUESSES", NUM_GUESSES))
        self.num_guesses = num_guesses

        if guess_len is None:
            guess_len = int(os.environ.get("GUESS_LEN", GUESS_LEN))
        self.guess_len = guess_len
