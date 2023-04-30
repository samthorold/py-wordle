from search.minimax import Node


def alphabeta(node: Node, a: Node, b: Node) -> Node:
    if node.is_terminal():
        return node

    best_node = node.minimum() if node.is_maximising() else node.maximum()

    for child in node.children():
        if node.is_maximising():
            best_node = max(best_node, alphabeta(child, a, b))
            if best_node > b:
                break
            a = max(a, best_node)
        else:
            best_node = min(best_node, alphabeta(child, a, b))
            if best_node < a:
                break
            b = min(b, best_node)

    return best_node
