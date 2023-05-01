from __future__ import annotations
from enum import Enum
from typing import Iterator


class Status(Enum):
    MISSING = "."
    PRESENT = "-"
    CORRECT = "="


class Player(Enum):
    X = "x"
    O = "o"


class GuessStatus:
    @classmethod
    def from_string(cls, string: str) -> GuessStatus:
        return cls([Status(s) for s in string])

    def __init__(self, status: list[Status]):
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
