from __future__ import annotations
from typing import Iterator, Sequence

import search
from wordle.models import CORRECT_GUESS, Guess, GuessStatus, Player
from wordle.evaluate import evaluate, _score
from wordle.prune import prune

HEURISTICS = ["sired", "about"]


class Board:
    @classmethod
    def from_string(
        cls,
        words: set[str],
        moves: Sequence[str],
        statuses: Sequence[str],
        num_guesses: int,
        guess_len: int,
        player: Player = Player.X,
        depth: int = 0,
    ) -> Board:
        gs = [Guess(g) for g in moves]
        ss = [GuessStatus.from_string(s) for s in statuses]
        return Board(
            words=words,
            moves=gs,
            statuses=ss,
            num_guesses=num_guesses,
            guess_len=guess_len,
            player=player,
            depth=depth,
        )

    def __init__(
        self,
        words: set[str],
        moves: list[Guess],
        statuses: list[GuessStatus],
        num_guesses: int,
        guess_len: int,
        player: Player = Player.X,
        depth: int = 0,
        is_min: bool = False,
        is_max: bool = False,
        heuristics: list[str] | None = None,
    ):
        self.words = words
        self.moves = moves
        self.statuses = statuses
        self.player = player
        self.depth = depth
        self.is_min = is_min
        self.is_max = is_max
        self.num_guesses = num_guesses
        self.guess_len = guess_len
        self.heuristics = HEURISTICS if heuristics is None else heuristics

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
                s += " " * (self.guess_len + 1)
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
            num_guesses=self.num_guesses,
            guess_len=self.guess_len,
        )

    def maximum(self) -> Board:
        return Board(
            words=set(),
            moves=[],
            statuses=[],
            is_max=True,
            num_guesses=self.num_guesses,
            guess_len=self.guess_len,
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
        words = prune(words=self.words, guesses=self.moves, statuses=statuses)
        return Board(
            words=words,
            moves=self.moves,
            statuses=statuses,
            player=self.next_player(),
            num_guesses=self.num_guesses,
            guess_len=self.guess_len,
        )

    def is_terminal(self) -> bool:
        if self.is_min or self.is_max:
            return False
        run_out_of_guesses = len(self.statuses) == self.num_guesses
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
            heuristics=self.heuristics,
            num_guesses=self.num_guesses,
            guess_len=self.guess_len,
        )

        return new_board

    def children(self) -> Iterator[Board]:
        if self.is_terminal():
            return
        is_max = self.is_maximising()
        words = self.words
        if not is_max:
            words = words - set([str(self.moves[-1])])
            words = prune(
                words=self.words,
                guesses=self.moves,
                statuses=self.statuses,
            )
        for word in words:
            if is_max:
                yield self.move(move=Guess(word), words=set(words))
            else:
                yield self.move(
                    move=evaluate(Guess(word).guess, self.moves[-1].guess),
                    words=set(words),
                )

    def heuristic(self) -> str | None:
        if not self.heuristics:
            return None
        for h in self.heuristics:
            if h in self.words:
                return h
        return None

    def guess(self, soft: bool = True) -> Board:
        maybe_move = self.heuristic()
        if maybe_move:
            move = Guess(maybe_move)
            self.heuristics.remove(maybe_move)
        else:
            variation = search.alphabeta(
                self,
                a=self.minimum(),
                b=self.maximum(),
                soft=soft,
            )
            move = variation.moves[len(self.moves)]
        return self.move(move, self.words)
