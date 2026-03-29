from math import inf

WIN_LINES = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

def winner(board):
    for a,b,c in WIN_LINES:
        if board[a] != ' ' and board[a] == board[b] == board[c]:
            return board[a]
    return None

def terminal(board):
    return winner(board) is not None or all(c != ' ' for c in board)

def utility(board):
    w = winner(board)
    if w == 'X': return 1
    if w == 'O': return -1
    return 0

def actions(board):
    return [i for i,c in enumerate(board) if c == ' ']

def player(board):
    x = sum(c == 'X' for c in board)
    o = sum(c == 'O' for c in board)
    return 'X' if x == o else 'O'

def result(board, move):
    b = board[:]
    b[move] = player(board)
    return b

def minimax(board):
    turn = player(board)
    if turn == 'X':
        value, move = max_value(board, -inf, inf)
    else:
        value, move = min_value(board, -inf, inf)
    return move

def max_value(board, alpha, beta):
    if terminal(board): return utility(board), None
    v, best_move = -inf, None
    for m in actions(board):
        v2, _ = min_value(result(board, m), alpha, beta)
        if v2 > v:
            v, best_move = v2, m
        alpha = max(alpha, v)
        if v >= beta: break
    return v, best_move

def min_value(board, alpha, beta):
    if terminal(board): return utility(board), None
    v, best_move = inf, None
    for m in actions(board):
        v2, _ = max_value(result(board, m), alpha, beta)
        if v2 < v:
            v, best_move = v2, m
        beta = min(beta, v)
        if v <= alpha: break
    return v, best_move

def print_board(board):
    rows = [' | '.join(board[r:r+3]) for r in (0,3,6)]
    print('\n---------\n'.join(rows))

def play():
    board = [' '] * 9
    while not terminal(board):
        print_board(board)
        if player(board) == 'O':  # Human as O
            mv = int(input("Enter your move (0-8): "))
            if board[mv] == ' ':
                board[mv] = 'O'
            else:
                print("Invalid move!")
        else:
            mv = minimax(board)
            board[mv] = 'X'
            print(f"AI plays {mv}")
    print_board(board)
    w = winner(board)
    print("Result:", "Draw" if w is None else f"{w} wins")

play()