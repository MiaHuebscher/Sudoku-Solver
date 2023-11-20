import numpy as np
from collections import Counter
from evo import Environment
NUMS = list(range(1, 10))


def create_board(game_str):
    board = []
    for start_i in range(0, 73, 9):
        end_i = start_i + 9
        board.append([int(num) for num in list(game_str[start_i:end_i])])

    return board


def count_blanks(board):
    zero_count = 0
    for row in board:
        if 0 in row:
            num_occs = Counter(row)
            zero_occs = num_occs[0]
            zero_count += zero_occs
        else:
            pass

    return zero_count


def switch_rows_cols(board):
    new_board = []
    for i in range(9):
        new_row = []
        for row in board:
            new_row.append(row[i])
        new_board.append(new_row)

    return new_board


def switch_boxes_rows(board):
    new_board = []
    first_row_index = 0
    next_row_index = 3
    for i in range(3):
        first_row = []
        sec_row = []
        third_row = []
        for row in board[first_row_index:next_row_index]:
            first_col_index = 0
            next_col_index = 3
            first_row += row[first_col_index:next_col_index]
            first_col_index += 3
            next_col_index += 3
            sec_row += row[first_col_index:next_col_index]
            first_col_index += 3
            next_col_index += 3
            third_row += row[first_col_index:next_col_index]

        new_board.append(first_row)
        new_board.append(sec_row)
        new_board.append(third_row)

        first_row_index += 3
        next_row_index += 3

    return new_board


def count_row_conflicts(board):
    conflicts = 0
    for row in board:
        for num in NUMS:
            if len(np.where(row == num)[0]) > 1:
                conflicts += 1
    return conflicts


def count_col_conflicts(board):
    board = switch_rows_cols(board)
    conflicts = count_row_conflicts(board)
    return conflicts


def count_box_conflicts(board):
    board = switch_boxes_rows(board)
    conflicts = count_row_conflicts(board)
    return conflicts


def fill_one_in_row(board):
    for row in board:
        num_occs = Counter(row)
        if num_occs[0] == 1:
            zero_idx = row.index(0)
            for num in NUMS:
                if num not in row:
                    missing = num
                    row[zero_idx] = missing
    return board


def fill_one_in_col(board):
    board = switch_rows_cols(board)
    board = fill_one_in_row(board)
    board = switch_rows_cols(board)
    return board


def fill_one_in_box(board):
    board = switch_boxes_rows(board)
    board = fill_one_in_row(board)
    board = switch_boxes_rows(board)
    return board


if __name__ == "__main__":

    # Create a population
    E = Environment()

    # Register the fitness criteria (objectives) with the evo framework
    E.add_fitness_criteria('blanks', count_blanks)
    E.add_fitness_criteria('row conflicts', count_row_conflicts)
    E.add_fitness_criteria('column conflicts', count_col_conflicts)
    E.add_fitness_criteria('subgrid conflicts', count_box_conflicts)

    # Register all the agents with the evo framework
    E.add_agent('fill one in row', fill_one_in_row, 1)
    E.add_agent('fill one in column', fill_one_in_col, 1)
    E.add_agent('fill one in subgrid', fill_one_in_box, 1)

    # Create the board and add it to the population
    game_str = "630542781812367594007809620480095207751020849206780015074206900368951472925478036"
    board = create_board(game_str)
    E.add_solution(board)

    # Run the evolver
    E.evolve(n=20000)

