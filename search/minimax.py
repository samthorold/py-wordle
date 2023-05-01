from search.node import Node


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
