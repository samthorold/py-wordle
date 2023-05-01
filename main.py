from wordle.wordle import wordle

if __name__ == "__main__":
    words = [
        "abbot",
        "scorn",
        "today",
        "rider",
        "dizzy",
        "crime",
        "rakes",
        "clear",
        "leech",
        "burnt",
        "monic",
        "motto",
        "noose",
        "maxim",
        "crate",
    ]
    with open("words/words-tiny.txt") as fh:
        words = fh.read().split("\n")
    # board = wordle(words, "allay", initial_guess="crate", soft=True)
    results = []
    for i, word in enumerate(words):
        print(word)
        board = wordle(words, word, initial_guess="crate", soft=True)
        # print(board)
        results.append(board.score())
        if i and not i % 25:
            print(len([r for r in results if r == 10]), len(results))
