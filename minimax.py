from typing import Any, Iterator, Protocol, Self


class Node(Protocol):
    """Comparison operators allows users to rank on more than just score."""

    moves: list[Any]

    def __gt__(self, other: Self) -> bool:
        return self.score() > other.score()

    def __lt__(self, other: Self) -> bool:
        return self.score() < other.score()

    def score(self) -> int:
        ...

    def is_terminal(self) -> bool:
        ...

    def children(self) -> Iterator[Self]:
        ...

    def is_maximising(self) -> bool:
        ...

    def minimum(self) -> Self:
        ...

    def maximum(self) -> Self:
        ...


def minimax(node: Node) -> Node:
    if node.is_terminal():
        return node

    best_node = node.minimum() if node.is_maximising() else node.maximum()

    for child in node.children():
        if node.is_maximising():
            best_node = max(best_node, minimax(child))
        else:
            best_node = min(best_node, minimax(child))

    return best_node
