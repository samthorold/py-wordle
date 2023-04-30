from __future__ import annotations
from enum import Enum
import functools
from typing import Iterable, Iterator, Sequence

import search


GUESS_LEN = 5


class Status(Enum):
    MISSING = "."
    PRESENT = "-"
    CORRECT = "="


# only cos isinstance in Board.move
class Guess:
    def __init__(self, guess: str):
        if len(guess) != GUESS_LEN:
            raise ValueError(f"Guess '{guess}' must be length {GUESS_LEN}.")
        self._guess = guess

    def __iter__(self) -> Iterator[str]:
        return iter(self._guess)

    def __getitem__(self, idx):
        return self._guess[idx]

    def __hash__(self):
        return hash(self._guess)

    def __str__(self) -> str:
        return self._guess

    def __contains__(self, o: str) -> bool:
        return o in self._guess


class GuessStatus:
    @classmethod
    def from_string(cls, string: str) -> GuessStatus:
        return cls([Status(s) for s in string])

    def __init__(self, status: list[Status]):
        if len(status) != GUESS_LEN:
            raise ValueError(f"Status'{status}' must be length {GUESS_LEN}.")
        self._status = status

    def __iter__(self) -> Iterator[Status]:
        return iter(self._status)

    def __hash__(self):
        return hash(tuple(self._status))

    def __str__(self) -> str:
        return "".join(s.value for s in self._status)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GuessStatus):
            raise NotImplemented
        return self._status == other._status


CORRECT_GUESS = GuessStatus([Status.CORRECT] * GUESS_LEN)


SCORES = {
    Status.MISSING: 0,
    Status.PRESENT: 1,
    Status.CORRECT: 2,
}


class Player(Enum):
    X = "x"
    O = "o"


class Board:
    @classmethod
    def from_string(
        cls,
        words: set[str],
        moves: Sequence[str],
        statuses: Sequence[str],
        player: Player = Player.X,
        depth: int = 0,
    ) -> Board:
        gs = [Guess(g) for g in moves]
        ss = [GuessStatus.from_string(s) for s in statuses]
        return Board(
            words=words,
            moves=gs,
            statuses=ss,
            player=player,
            depth=depth,
        )

    def __init__(
        self,
        words: set[str],
        moves: list[Guess],
        statuses: list[GuessStatus],
        player: Player = Player.X,
        depth: int = 0,
        is_min: bool = False,
        is_max: bool = False,
    ):
        words = update_words(words, guesses=moves, statuses=statuses)
        self.words = words
        self.moves = moves
        self.statuses = statuses
        self.player = player
        self.depth = depth
        self.is_min = is_min
        self.is_max = is_max

    def __gt__(self, other: Board) -> bool:
        return self.score() > other.score()

    def __lt__(self, other: Board) -> bool:
        return self.score() < other.score()

    def __ge__(self, other: Board) -> bool:
        return self.score() >= other.score()

    def __le__(self, other: Board) -> bool:
        return self.score() <= other.score()

    def is_maximising(self) -> bool:
        return self.player == Player.X

    def minimum(self) -> Board:
        return Board(
            words=set(),
            moves=[],
            statuses=[],
            is_min=True,
        )

    def maximum(self) -> Board:
        return Board(
            words=set(),
            moves=[],
            statuses=[],
            is_max=True,
        )

    def __str__(self) -> str:
        guesses = "\n".join([str(row) for row in self.moves])
        if self.statuses and (len(self.statuses) == len(self.moves)):
            status = "\n" + f"{self.statuses[-1]}"
        else:
            status = ""
        return f"{guesses}{status}"

    def move(self, move: Guess | GuessStatus) -> Board:
        if isinstance(move, Guess):
            if move._guess not in self.words:
                raise ValueError(
                    f"Guess '{move._guess}' not in words, might struggle."
                )
            moves = self.moves + [move]
            statuses = self.statuses
        else:
            moves = [m for m in self.moves]
            statuses = self.statuses + [move]

        if (not self.is_maximising()) and self.moves:
            words = self.words - set([str(self.moves[-1])])
        else:
            words = self.words

        new_board = Board(
            words=words,
            moves=moves,
            statuses=statuses,
            player=self.next_player(),
            depth=self.depth + 1,
        )

        return new_board

    def score(self) -> int:
        if self.is_min:
            return -100
        if self.is_max:
            return 100
        if not self.statuses:
            return 0
        return _score(self.statuses[-1])

    def is_terminal(self) -> bool:
        if self.is_min or self.is_max:
            return False
        run_out_of_guesses = len(self.statuses) == 6
        correct = any(s == CORRECT_GUESS for s in self.statuses)
        return run_out_of_guesses or correct

    def next_player(self) -> Player:
        return Player.X if self.player == Player.O else Player.O

    def children(self) -> Iterator[Board]:
        if self.is_terminal():
            return
        words = sorted(self.words, key=lambda w: -len(set(w)))
        for word in words:
            if self.is_maximising():
                yield self.move(Guess(word))
            else:
                yield self.move(evaluate(Guess(word), self.moves[-1]))

    def lowest_scoring_move(self) -> Guess:
        if not self.moves and "crate" in self.words:
            return Guess("crate")
        children = list(self.children())
        ch = children[0]
        for c in children[1:]:
            if c.score() < ch.score():
                ch = c
        return ch.moves[-1]


def present(aim: Guess, guess: Guess, guessc: str, i: int) -> Status:
    if i > 0:
        count_aimc = len([c for c in aim if c == guessc])
        count_stats = len([c for c in guess[:i] if c == guessc])
        if count_aimc <= count_stats:
            return Status.MISSING
    return Status.PRESENT


@functools.cache
def evaluate(aim: Guess, guess: Guess) -> GuessStatus:
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
def _score(gs: GuessStatus) -> int:
    return sum(SCORES[s] for s in gs)


def update_words(
    words: set[str],
    guesses: list[Guess],
    statuses: list[GuessStatus],
) -> set[str]:
    if not guesses:
        return words

    for guess, status in zip(guesses, statuses):
        if status == CORRECT_GUESS:
            return set([str(guess)])
        else:
            words = set([w for w in words if w != str(guess)])

        for i, (c, s) in enumerate(zip(str(guess), str(status))):
            match s:
                case Status.CORRECT.value:
                    words = set([w for w in words if w[i] == c])
                case Status.PRESENT.value:
                    words = set([w for w in words if c in w and w[i] != c])
                case Status.MISSING.value:
                    # But, I use missing when there are present characters
                    # but too many of them
                    # So, if the letter is present or correct anywhere
                    # elsewhere skip this missing filter
                    stats = [s for s, c_ in zip(str(status), str(guess)) if c_ == c]
                    if any(s != Status.MISSING.value for s in stats):
                        words = set([w for w in words if c in w and w[i] != c])
                        continue
                    words = set([w for w in words if c not in w])
    return words


def main(words: set[str], aim: str) -> None:
    if aim not in words:
        raise ValueError("Aim not in words, might struggle.")

    board = Board(
        words=words,
        moves=[],
        statuses=[],
    )

    while True:
        if board.score() < 5:
            move = board.lowest_scoring_move()
            board = board.move(move)
        else:
            variation = search.alphabeta(board, a=board.minimum(), b=board.maximum())
            board = board.move(variation.moves[len(board.moves)])
        status = evaluate(Guess(aim), board.moves[-1])
        board = board.move(status)
        print(board)
        if board.is_terminal():
            print(board.score())
            break
        print()


if __name__ == "__main__":
    words = [
        "abbot",
        "scorn",
        "today",
        "rider",
        "dizzy",
        "crime",
        "rakes",
        "clear",
        "leech",
        "burnt",
        "monic",
        "motto",
        "noose",
        "maxim",
    ]
    with open("words.txt") as fh:
        words = fh.read().split("\n")

    # main(set(words), "burnt")
    main(set(words), "fizzy")
