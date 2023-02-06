"""
Code that generates and solves a game of sudoku
"""
import numpy as np
from evo import Environment
NUMS = list(range(1, 10))


def create_board(game):
    board = []
    for s in range(0, 73, 9):
        e = s + 9
        board.append([int(num) for num in list(game[s:e])])

    return board


def fill_rows(board):
    for row in board:
        count = 0
        for n in row:
            if n == 0:
                count += 1
        if count == 1:
            zero_idx = row.index(0)
            for num in NUMS:
                if num not in row:
                    miss = num
                    row[zero_idx] = miss
    return board


def fill_cols(board):
    for idx in range(0,9):
        col = []
        for lst in board:
            col.append(lst[idx])
        count = 0
        for c_idx in range(len(col)):
            if col[c_idx] == 0:
                miss_idx = idx
                b_idx = c_idx
                count += 1
        if count == 1:
            for num in NUMS:
                if num not in col:
                    board[b_idx][miss_idx] = num
    return board


def fill_miss_row(board):
    for b_idx in range(len(board)):
        miss_idx = [board[b_idx].index(num) for num in board[b_idx] if num == 0]
        miss = [num for num in NUMS if num not in board[b_idx]]
        dct = {}
        for num in miss:
            for idx in miss_idx:
                x = 'can'
                for row in board:
                    if row[idx] == num:
                        x = 'cant'
                if x == 'can':
                    board[b_idx][idx] = num

    return board


def check(board):
    for row in board:
        for num in NUMS:
            if num not in row:
                return 'unsolved'
    return 'solved'


if '__main__' == __name__:
    """
    game 1
    
    game = "431295806862017594700864320246053708108070405305140269084736002513420687607581943"
    board = create_board(game)
    board = fill_rows(board)
    board = fill_cols(board)
    board = fill_rows(board)
    board = fill_miss_row(board)
    board = fill_rows(board)
    board = fill_cols(board)
    print(check(board))
    """
    game = "630542781812367594007809620480095207751020849206780015074206900368951472925478036"
    board = create_board(game)
    print(board)
    while check(board) == 'unsolved':
        board = fill_rows(board)
        board = fill_cols(board)
        board = fill_miss_row(board)
        print(board)

    print(board)








