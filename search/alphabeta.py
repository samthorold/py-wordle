from search.node import Node


def alphabeta(node: Node, a: Node, b: Node, soft: bool = True) -> Node:
    if node.is_terminal():
        return node

    gt_op = "__ge__" if soft else "__gt__"
    lt_op = "__le__" if soft else "__lt__"

    best_node = node.minimum() if node.is_maximising() else node.maximum()

    for child in node.children():
        if node.is_maximising():
            best_node = max(best_node, alphabeta(node=child, a=a, b=b, soft=soft))
            a = max(a, best_node)
            if getattr(best_node, gt_op)(b):
                break
        else:
            best_node = min(best_node, alphabeta(node=child, a=a, b=b, soft=soft))
            b = min(b, best_node)
            if getattr(best_node, lt_op)(a):
                break

    return best_node
