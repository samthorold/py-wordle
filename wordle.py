from __future__ import annotations
from enum import Enum
import functools
from typing import Iterator, Sequence

import search


NUM_GUESSES = 6
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
        self.guess = guess

    def __iter__(self) -> Iterator[str]:
        return iter(self.guess)

    def __str__(self) -> str:
        return self.guess

    def __contains__(self, o: str) -> bool:
        return o in self.guess

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.guess == other
        if isinstance(other, Guess):
            return self.guess == other.guess
        raise NotImplemented


class GuessStatus:
    @classmethod
    def from_string(cls, string: str) -> GuessStatus:
        return cls([Status(s) for s in string])

    def __init__(self, status: list[Status]):
        if len(status) != GUESS_LEN:
            raise ValueError(f"Status'{status}' must be length {GUESS_LEN}.")
        self.status = status

    def __iter__(self) -> Iterator[Status]:
        return iter(self.status)

    def __str__(self) -> str:
        return "".join(s.value for s in self.status)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GuessStatus):
            raise NotImplemented
        return self.status == other.status


CORRECT_GUESS = GuessStatus.from_string("=====")
TOTALLY_WRONG_GUESS = GuessStatus.from_string(".....")


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

    def __str__(self) -> str:
        s = ""
        for i, guess in enumerate(self.moves):
            s += str(guess)
            if len(self.statuses) > i:
                s += " " + "".join(s.value for s in self.statuses[i])
            else:
                s += " " * (GUESS_LEN + 1)
            if i == (len(self.moves) - 1):
                s += f"{len(self.words):>6}"
            s += "\n"
        return s

    def is_maximising(self) -> bool:
        return self.player == Player.X

    def next_player(self) -> Player:
        return Player.X if self.player == Player.O else Player.O

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

    def score(self) -> int:
        if self.is_min:
            return -100
        if self.is_max:
            return 100
        if not self.statuses:
            return 0
        return _score(tuple(self.statuses[-1].status))

    def evaluate(self, aim: str) -> Board:
        statuses = self.statuses + [evaluate(aim, self.moves[-1].guess)]
        words = update_words(words=self.words, guesses=self.moves, statuses=statuses)
        return Board(
            words=words,
            moves=self.moves,
            statuses=statuses,
            player=self.next_player(),
        )

    def is_terminal(self) -> bool:
        if self.is_min or self.is_max:
            return False
        run_out_of_guesses = len(self.statuses) == NUM_GUESSES
        correct = any(s == CORRECT_GUESS for s in self.statuses)
        return run_out_of_guesses or correct

    def move(self, move: Guess | GuessStatus, words: set[str]) -> Board:
        words = self.words
        if isinstance(move, Guess):
            if move.guess not in self.words:
                raise ValueError(
                    f"Guess '{move.guess}' not in words, might struggle."
                )
            moves = self.moves + [move]
            statuses = self.statuses
        else:
            moves = [m for m in self.moves]
            statuses = self.statuses + [move]

        new_board = Board(
            words=words,
            moves=moves,
            statuses=statuses,
            player=self.next_player(),
            depth=self.depth + 1,
        )

        return new_board

    def children(self) -> Iterator[Board]:
        if self.is_terminal():
            return
        is_max = self.is_maximising()
        words = self.words
        if not is_max:
            words = words - set([str(self.moves[-1])])
            words = update_words(
                words=self.words,
                guesses=self.moves,
                statuses=self.statuses,
            )
            words = sorted(words, key=lambda w: -len(set(w)))
        else:
            words = sorted(words, key=lambda w: len(set(w)))
        for word in words:
            if is_max:
                yield self.move(move=Guess(word), words=set(words))
            else:
                yield self.move(
                    move=evaluate(Guess(word).guess, self.moves[-1].guess),
                    words=set(words),
                )

    def heuristic(self) -> Guess | None:
        crate, mogul, djins = "crate", "mogul", "djins"
        if not self.moves and crate in self.words:
            return Guess(crate)
        if (
            len(self.statuses) == 1
            and self.statuses[-1] == TOTALLY_WRONG_GUESS
            and mogul in self.words
        ):
            return Guess(mogul)
        if (
            len(self.statuses) == 2
            and self.statuses[-1] == TOTALLY_WRONG_GUESS
            and djins in self.words
        ):
            return Guess(djins)

    def guess(self) -> Board:
        maybe_move = self.heuristic()
        if maybe_move:
            move = maybe_move
        else:
            variation = search.alphabeta(self, a=self.minimum(), b=self.maximum())
            move = variation.moves[len(self.moves)]
        return self.move(move, self.words)


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


def update_words(
    words: set[str],
    guesses: list[Guess],
    statuses: list[GuessStatus],
) -> set[str]:
    # noop if either guesses or statuses is empty
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


def main(words: set[str], aim: str) -> Board:
    if aim not in words:
        raise ValueError("Aim not in words, might struggle.")

    board = Board(
        words=words,
        moves=[],
        statuses=[],
    )

    while True:
        board = board.guess()
        board = board.evaluate(aim)
        print(board)
        if board.is_terminal():
            break
    return board


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
    with open("words-tiny.txt") as fh:
        words = fh.read().split("\n")

    board = main(set(words), "fizzy")
    print(board)

    # results = []
    # for i, word in enumerate(words):
    #     print(word)
    #     results.append(main(set(words), word))
    #     if i and not i % 25:
    #         print(len([r for r in results if r == 10]), len(results))
