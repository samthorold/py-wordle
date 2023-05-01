from __future__ import annotations
from typing import Iterator, Sequence

import search
from wordle.models import CORRECT_GUESS, GuessStatus, Player
from wordle.evaluate import evaluate, _score
from wordle.prune import prune


class Board:
    @classmethod
    def from_string(
        cls,
        words: set[str],
        moves: Sequence[str],
        statuses: Sequence[str],
        initial_guess: str,
        player: Player = Player.X,
    ) -> Board:
        gs = [g for g in moves]
        ss = [GuessStatus.from_string(s) for s in statuses]
        return Board(
            words=words,
            moves=gs,
            statuses=ss,
            initial_guess=initial_guess,
            player=player,
        )

    def __init__(
        self,
        words: set[str],
        moves: list[str],
        statuses: list[GuessStatus],
        initial_guess: str,
        player: Player = Player.X,
        is_min: bool = False,
        is_max: bool = False,
    ):
        self.words = words
        self.moves = moves
        self.statuses = statuses
        self.player = player
        self.is_min = is_min
        self.is_max = is_max
        self.initial_guess = initial_guess

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
                s += " " * 7
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
            initial_guess=self.initial_guess,
        )

    def maximum(self) -> Board:
        return Board(
            words=set(),
            moves=[],
            statuses=[],
            is_max=True,
            initial_guess=self.initial_guess,
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
        statuses = self.statuses + [evaluate(aim, self.moves[-1])]
        words = prune(words=self.words, guesses=self.moves, statuses=statuses)
        return Board(
            words=words,
            moves=self.moves,
            statuses=statuses,
            player=self.next_player(),
            initial_guess=self.initial_guess,
        )

    def is_terminal(self) -> bool:
        if self.is_min or self.is_max:
            return False
        run_out_of_guesses = len(self.statuses) == 6
        correct = any(s == CORRECT_GUESS for s in self.statuses)
        return run_out_of_guesses or correct

    def move(self, move: str) -> Board:
        words = self.words
        if move not in self.words:
            raise ValueError(f"Guess '{move}' not in words, might struggle.")

        new_board = Board(
            words=words,
            moves=self.moves + [move],
            statuses=self.statuses,
            player=self.next_player(),
            initial_guess=self.initial_guess,
        )

        return new_board

    def children(self) -> Iterator[Board]:
        if self.is_terminal():
            return
        is_max = self.is_maximising()
        for word in self.words:
            if is_max:
                yield self.move(move=word)
            else:
                yield self.evaluate(aim=word)

    def heuristic(self) -> str | None:
        if not self.moves:
            return "crate"
        return None

    def guess(self, soft: bool = True) -> Board:
        maybe_move = self.heuristic()
        if maybe_move := self.heuristic():
            move = maybe_move
        else:
            variation = search.alphabeta(
                self,
                a=self.minimum(),
                b=self.maximum(),
                soft=soft,
            )
            move = variation.moves[len(self.moves)]
        return self.move(move)
