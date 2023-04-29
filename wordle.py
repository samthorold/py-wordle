from __future__ import annotations
from enum import Enum
import functools
from typing import Iterator, Sequence

from minimax import minimax


class Status(Enum):
    MISSING = "."
    PRESENT = "-"
    CORRECT = "="


# only cos isinstance in Board.move
class Guess:
    def __init__(self, guess: str):
        self._guess = guess

    def __iter__(self):
        return iter(self._guess)

    def __getitem__(self, idx):
        return self._guess[idx]

    def __str__(self) -> str:
        return self._guess


GuessStatus = tuple[Status, Status, Status, Status, Status]

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
        words: Sequence[str],
        moves: Sequence[str],
        statuses: Sequence[str],
        player: Player = Player.X,
        depth: int = 0,
    ) -> Board:
        gs = [Guess(g) for g in moves]
        ss = tuple([tuple([Status(x) for x in s]) for s in statuses])
        return Board(
            words=words,
            moves=gs,
            statuses=ss,
            player=player,
            depth=depth,
        )

    def __init__(
        self,
        words: Sequence[str],
        moves: list[Guess],
        statuses: tuple[GuessStatus, ...],
        player: Player = Player.X,
        depth: int = 0,
        is_min: bool = False,
        is_max: bool = False,
    ):
        self.words = update_words(
            words=words,
            guesses=moves,
            statuses=statuses,
        )
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

    def is_maximising(self) -> bool:
        return self.player == Player.X

    def minimum(self) -> Board:
        return Board(
            words=[],
            moves=[],
            statuses=tuple(),
            is_min=True,
        )

    def maximum(self) -> Board:
        return Board(
            words=[],
            moves=[],
            statuses=tuple(),
            is_max=True,
        )

    def __str__(self) -> str:
        guesses = "\n".join([str(row) for row in self.moves])
        if self.statuses and (len(self.statuses) == len(self.moves)):
            status = "\n" + ", ".join([s.value for s in self.statuses[-1]])
        else:
            status = ""
        return f"{guesses}{status}"

    def move(self, move: Guess | GuessStatus) -> Board:
        if isinstance(move, Guess):
            moves = list(self.moves) + [move]
            statuses = self.statuses
        else:
            moves = [m for m in self.moves]
            statuses = tuple(list(self.statuses) + [move])

        return Board(
            words=self.words,
            moves=moves,
            statuses=statuses,
            player=self.next_player(),
            depth=self.depth + 1 if not self.is_maximising() else 0,
        )

    def score(self) -> int:
        if self.is_min:
            return -100
        if self.is_max:
            return 100
        return sum(SCORES[s] for s in self.statuses[-1])

    def is_terminal(self) -> bool:
        run_out_of_guesses = len(self.statuses) == 6
        correct = any(s == tuple([Status.CORRECT] * 5) for s in self.statuses)
        return run_out_of_guesses or correct

    def next_player(self) -> Player:
        return Player.X if self.player == Player.O else Player.O

    def children(self) -> Iterator[Board]:
        if self.is_terminal():
            return
        for word in self.words:
            if self.is_maximising():
                yield self.move(Guess(word))
            else:
                yield self.move(evaluate(Guess(word), self.moves[-1]))


def update_words(
    words: Sequence[str],
    guesses: list[Guess],
    statuses: tuple[GuessStatus, ...],
) -> Sequence[str]:
    if not guesses:
        return words

    for guess, status in zip(guesses, statuses):
        if status == tuple([Status.CORRECT] * 5):
            return ["".join(guess)]
        else:
            words = [w for w in words if w != "".join(guess)]

        for i, (c, s) in enumerate(zip(guess, status)):
            match s:
                case Status.CORRECT:
                    words = [w for w in words if w[i] == c]
                case Status.PRESENT:
                    words = [w for w in words if c in w and w[i] != c]
                case Status.MISSING:
                    # But, I use missing when there are present characters
                    # but too many of them
                    # So, if the letter is present or correct anywhere
                    # elsewhere skip this missing filter
                    stats = [s for s, c_ in zip(status, guess) if c_ == c]
                    if any(s != Status.MISSING for s in stats):
                        words = [w for w in words if c in w and w[i] != c]
                        continue
                    words = [w for w in words if c not in w]
    return words


def present(aim: Guess, guess: Guess, guessc: str, i: int) -> Status:
    if i > 0:
        count_aimc = len([c for c in aim if c == guessc])
        count_stats = len([c for c in guess[:i] if c == guessc])
        if count_aimc <= count_stats:
            return Status.MISSING
    return Status.PRESENT


@functools.cache
def evaluate(aim: Guess, guess: Guess) -> GuessStatus:
    stats: list[Status] = []
    for i, (aimc, guessc) in enumerate(zip(aim, guess)):
        if aimc == guessc:
            stats.append(Status.CORRECT)
        elif guessc in aim:
            stats.append(present(aim=aim, guess=guess, guessc=guessc, i=i))
        else:
            stats.append(Status.MISSING)
    return tuple([stats[0], stats[1], stats[2], stats[3], stats[4]])


def main(words: Sequence[str], aim: str) -> None:
    if aim not in words:
        raise ValueError("Aim not in words, might struggle.")

    board = Board(
        words=words,
        moves=[],
        statuses=tuple(),
    )

    while True:
        variation = minimax(board)
        board = board.move(variation.moves[board.depth])
        status = evaluate(Guess(aim), board.moves[-1])
        board = board.move(status)
        print(board)
        if board.is_terminal():
            print(board.score())
            break
        print()


if __name__ == "__main__":
    with open("words-min.txt") as fh:
        words = fh.read().split("\n")
    # words = [
    #     "abbot",
    #     "scorn",
    #     "today",
    #     "rider",
    #     "dizzy",
    #     "crime",
    #     "rakes",
    #     "clear",
    #     "leech",
    #     "burnt",
    #     "monic",
    #     "motto",
    #     "noose",
    # ]

    main(words, "maxim")
