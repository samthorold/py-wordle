from ttt.minimax import minimax
from ttt.ttt import Board, Player


def main() -> None:
    board = Board.from_string("." * 9, Player.O)
    while True:
        r, c = [int(m) for m in input("Move: ")]
        board = board.move((r, c))
        print(board.string())
        if board.is_terminal():
            print(board.score())
            break
        variation = minimax(board)
        board = board.move(variation.moves[board.depth])
        print(board.string())
        if board.is_terminal():
            print(board.score())
            break


if __name__ == "__main__":
    main()
