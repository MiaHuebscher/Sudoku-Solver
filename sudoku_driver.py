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


def fill_box(game):
    """Fill boxes that have positions that can be filled with missing numbers"""
    game = np.array(game)
    # Obtain the boxes in the Sudoku game
    for row_start in range(0, 9, 3):
        row_end = row_start + 3
        for col_start in range(0, 9, 3):
            col_end = col_start + 3
            box = game[row_start:row_end, col_start:col_end]
            # Locate the missing numbers and their locations
            zero_rows, zero_cols = np.where(box == 0)
            missing = [num for num in range(1, 10) if num not in box.reshape(9)]
            miss_dct = {}
            # Identify where the missing numbers could be placed in the box
            for num in missing:
                for row, col in zip(zero_rows, zero_cols):
                    real_row = row + row_start
                    real_col = col + col_start
                    if num not in game[real_row, :] and num not in game[:, real_col]:
                        if num not in miss_dct:
                            miss_dct[num] = [(real_row, real_col)]
                        else:
                            miss_dct[num].append((real_row, real_col))
            # Place numbers that only have one possible location in the box
            to_solve = [k for k, v in miss_dct.items() if len(v) == 1]
            for num in to_solve:
                row = miss_dct[num][0][0]
                col = miss_dct[num][0][1]
                game[row, col] = num

    return game


def advanced_fill(game):
    """For each possible number, place it in a position within a box based on the number's position in other boxes"""
    game = np.array(game)
    for num in range(1, 10):
        # Obtain a box in the game
        for row_start in range(0, 9, 3):
            row_end = row_start + 3
            for col_start in range(0, 9, 3):
                col_end = col_start + 3
                # Make a copy of the game so that test changes made are not permanent
                new_game = game.copy()
                box = new_game[row_start:row_end, col_start:col_end]
                # If the current number is not in the current box, find all places the number could be put in the box
                if num not in box.reshape(9):
                    zero_rows, zero_cols = np.where(box == 0)
                    update = []
                    for row, col in zip(zero_rows, zero_cols):
                        real_row = row + row_start
                        real_col = col + col_start
                        if num not in game[real_row, :] and num not in game[:, real_col]:
                            update.append((real_row, real_col))
                    # If all locations are in the same row or column, put the number in those places in the game copy
                    if len(update) > 1 and (all(row == [row for row, col in update][0] for row, col in update) or
                                            all(col == [col for row, col in update][0] for row, col in update)):
                        for change_row, change_col in update:
                            new_game[change_row, change_col] = num

                        # Loop through the game copy again and see if the placed numbers give us enough constraints to
                        # Place numbers in the real game
                        for r_start in range(0, 9, 3):
                            r_end = r_start + 3
                            for c_start in range(0, 9, 3):
                                c_end = c_start + 3
                                if r_start == row_start and c_start == col_start:
                                    pass
                                box = game[r_start:r_end, c_start:c_end]
                                # Locate all the places the number could be put
                                zero_rows, zero_cols = np.where(box == 0)
                                options = list(zip(zero_rows, zero_cols))
                                for row, col in zip(zero_rows, zero_cols):
                                    real_row = row + r_start
                                    real_col = col + c_start
                                    # If there is more than 1 count of the number in the same row or column of the
                                    # Location, remove the location as an option
                                    if list(new_game[real_row, :]).count(num) > 1 or \
                                            list(new_game[:, real_col]).count(num) > 1:
                                        options.remove((row, col))
                                # Place numbers that only have one possible location in the box, after checking if the
                                # Location has one occurrence of the same number in the same row or column
                                if len(options) == 1:
                                    row = options[0][0] + r_start
                                    col = options[0][1] + c_start
                                    if num not in game[row, :] and num not in game[:, col]:
                                        game[row, col] = num

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
    E.add_agent('fill box', fill_box, 1)
    E.add_agent('advanced fill', advanced_fill, 1)

    # Create the board and add it to the population
    """Source of Games: https://www.nytimes.com/puzzles/sudoku"""
    easy_nyt = '300010294152090000009723016006800403405130000000607120000000347083260000090071600'
    medium_nyt = '900104500007080060800903001003000600010400000708000200040307000000001400070000090'
    hard_nyt = '000090806040005012000600000032000008608003000000000057020700000001962000300050009'
    board = create_board(medium_nyt)
    E.add_solution(board)

    # Run the evolver
    E.evolve(n=30000)



