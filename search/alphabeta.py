from search.node import Node


def alphabeta(node: Node, a: Node, b: Node) -> Node:
    if node.is_terminal():
        return node

    best_node = node.minimum() if node.is_maximising() else node.maximum()

    for child in node.children():
        if node.is_maximising():
            best_node = max(best_node, alphabeta(child, a, b))
            a = max(a, best_node)
            if best_node >= b:
                break
        else:
            best_node = min(best_node, alphabeta(child, a, b))
            b = min(b, best_node)
            if best_node <= a:
                break

    return best_node
