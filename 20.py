
def check_winner(board):
    print(board)
    if board[0][0] == board[1][0] == board[2][0]: #pion1
        return board[0][0]
    elif board[0][1] == board[1][1] == board[2][1]: #pion2
        return board[0][1]
    elif board[0][1] == board[1][1] == board[2][1]: #pion3
        return board[0][2]
    elif board[0][0] == board[0][1] == board[0][2]: #poziom1
            return board[0][0]
    elif board[1][0] == board[1][1] == board[1][2]: #poziom2
        return board[1][0]
    elif board[2][0] == board[2][1] == board[2][2]: #poziom3
        return board[2][0]
    elif board[0][0] == board[1][1] == board[2][2]: #skos1
        return board[0][0]
    elif board[0][2] == board[1][1] == board[2][0]: #skos2
        return board[0][2]
    else:
        return "Draw"
