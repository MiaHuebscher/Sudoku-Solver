import numpy as np
from sudoku_evo import Environment
from collections import Counter


def create_board(string):
    """Constructs a Sudoku game from a String of numbers"""
    game_lst = [int(num) for num in string]
    game_board = np.array(game_lst).reshape((9, 9))
    return game_board


def count_blanks(game):
    """Counts the number of positions that need to be filled"""
    counts_dict = Counter(game.reshape(81))
    zero_count = counts_dict[0]
    return zero_count


def count_row_conflicts(game):
    """Counts the number of conflicts in the rows of the game"""
    return sum([1 for i in range(9) for j in range(1, 9) if len(np.where(game[i] == j)[0]) > 1])


def count_col_conflicts(game):
    """Counts the number of conflicts in the columns of the game"""
    game = np.array(game)
    game = game.T
    conflicts = count_row_conflicts(game)
    return conflicts


def count_box_conflicts(game):
    """Counts the number of conflicts in the boxes of the game"""
    game = switch_rows_boxes(game)
    conflicts = count_row_conflicts(game)
    return conflicts


def switch_rows_boxes(game):
    """Turns the boxes of the game into rows (which simultaneously turns the rows into the boxes)"""
    game = np.array(game)
    new_game = []

    # Create a loop that defines and updates the index slicing to redefine the rows of the game
    for row_start in range(0, 9, 3):
        row_end = row_start + 3
        for col_start in range(0, 9, 3):
            col_end = col_start + 3
            new_row = game[row_start:row_end, col_start:col_end].reshape(9)
            new_game.append(new_row)

    return np.array(new_game)


def fill_one_row(game):
    """Fill rows that are only missing one number - the easiest way to advance in the game"""
    # Identify rows only missing one number
    lst_missing_one = [i for i in range(len(game)) if len(np.where(game[i] == 0)[0]) == 1]
    for i in lst_missing_one:
        # Identify the column in the row that is missing the number and fill it in
        zero_idx = list(game[i]).index(0)
        missing = [num for num in range(1, 10) if num not in game[i]]
        game[i][zero_idx] = missing[0]
    return np.array(game)


def fill_one_col(game):
    """Fill cols that are only missing one number - the easiest way to advance in the game"""
    game = np.array(game)
    game = game.T
    game = fill_one_row(game)
    game = game.T
    return game


def fill_one_box(game):
    """Fill boxes that are only missing one number - the easiest way to advance in the game"""
    game = switch_rows_boxes(game)
    game = fill_one_row(game)
    game = switch_rows_boxes(game)
    return game


def fill_row(game):
    """Fill rows that have positions that can be filled with missing numbers"""
    # Locate all the locations of zeros in the matrix
    game = np.array(game)
    zero_rows, zero_cols = np.where(game == 0)

    # Loop through the rows of the matrix to fill in missing numbers
    for row_idx in range(len(game)):
        zeros = [item[1] for item in zip(zero_rows, zero_cols) if item[0] == row_idx]
        missing = [num for num in range(1, 10) if num not in game[row_idx]]
        # Construct a dictionary to track the number of places each missing number can be put
        miss_dct = {}
        for num in missing:
            # Check if they can fit in columns
            col_count = sum([1 for i in zeros if num not in game[:, i]])
            miss_dct[num] = col_count
        # If a missing number can only be put in one place, put it there
        to_solve = [k for k, v in miss_dct.items() if v == 1]
        for num in to_solve:
            pos = [i for i in zeros if num not in game[:, i]][0]
            # Check if num satisfies box requirements
            row_start = int(row_idx / 3) * 3
            col_start = int(pos / 3) * 3
            box_lst = game[row_start:row_start + 3, col_start:col_start + 3].reshape(9)
            if num not in box_lst:
                game[row_idx, pos] = num

    return game


def fill_col(game):
    """Fill columns that have positions that can be filled with missing numbers"""
    game = np.array(game)
    game = game.T
    game = fill_row(game)
    game = game.T
    return game


if __name__ == "__main__":
    # Create a population
    E = Environment()

    # Register the fitness criteria (objectives) with the evo framework
    E.add_fitness_criteria('blanks', count_blanks)
    E.add_fitness_criteria('row conflicts', count_row_conflicts)
    E.add_fitness_criteria('column conflicts', count_col_conflicts)
    E.add_fitness_criteria('subgrid conflicts', count_box_conflicts)

    # Register all the agents with the evo framework
    E.add_agent('fill one in row', fill_one_row, 1)
    E.add_agent('fill one in column', fill_one_col, 1)
    E.add_agent('fill one in subgrid', fill_one_box, 1)
    E.add_agent('fill row', fill_row, 1)
    E.add_agent('fill column', fill_col, 1)

    # Create the board and add it to the population
    game_str = '630542781812367594007809620480095207751020849206780015074206900368951472925478036'
    nyt_sudoku = '780006312264100897190082000000693000801500000056000400672009004009000731000057020'
    board = create_board(nyt_sudoku)
    E.add_solution(board)

    # Run the evolver
    E.evolve(n=30000)



