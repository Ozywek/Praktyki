def check_winner(board):
    # kolumny
    for j in range(len(board[0])):
        a = []
        for i in range(len(board)):
            a.append(board[i][j])
        if len(set(a)) == 1:
            return a[0]

    # wiersze
    for wiersz in board:
        if len(set(wiersz)) == 1:
            return wiersz[0]

    # skosy
    g = []
    for i in range(len(board)):
        g.append(board[i][i])
    if len(set(g)) == 1:
        return g[0]

    h = []
    for i in range(len(board)):
        h.append(board[i][len(board) - 1 - i])
    if len(set(h)) == 1:
        return h[0]
    return "Draw"


print(check_winner(board = [
    ["A", "V", "Z"],
    ["b", "Z", "N"],
    ["Z", "V", "Z"]
]))
