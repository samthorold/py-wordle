from typing import Any, Iterator, Protocol, Self


class Node(Protocol):
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

    def is_maximising_player(self) -> bool:
        ...

    def minimum(self) -> Self:
        ...

    def maximum(self) -> Self:
        ...


def minimax(node: Node) -> Node:
    if node.is_terminal():
        return node

    if node.is_maximising_player():
        best_node = node.minimum()
        for child in node.children():
            best_node = max(best_node, minimax(child))

    else:
        best_node = node.maximum()
        for child in node.children():
            best_node = min(best_node, minimax(child))

    return best_node
