from evo import Environment
import numpy as np
NUMS = list(range(1, 10))


def create_board(game):
    board = []
    for s in range(0, 73, 9):
        e = s + 9
        board.append([int(num) for num in list(game[s:e])])

    return np.array(board)


def blanks(sol):
    zero_count = 0
    for row in sol:
        for num in row:
            if num == 0:
                zero_count += 1
    return zero_count


def row_conflicts(sol):
    """returns the number of rows that duplications of one or more numbers"""
    conflicts = 0
    for row in sol:
        num_dct = {num: 0 for num in NUMS}
        for num in row:
            if num != 0:
                num_dct[num] += 1
        overallocations = ['overallocation' for val in num_dct.values() if val > 1]
        if overallocations:
            conflicts += 1

    return conflicts


def column_conflicts(sol):
    conflicts = 0
    for col in range(9):
        col_dct = {num: 0 for num in NUMS}
        for row in sol:
            if row[col] != 0:
                col_dct[row[col]] += 1
        overallocations = ['overallocation' for val in col_dct.values() if val > 1]
        if overallocations:
            conflicts += 1
    return conflicts


def subgrid_conflicts(sol):
    conflicts = 0
    for item in ['1a', '1b', '1c', '2a', '2b', '2c', '3a', '3b', '3c']:
        subg_dct = {num: 0 for num in NUMS}
        if item[1] == 'a':
            rs = 0
            re = 3
        elif item[1] == 'b':
            rs = 3
            re = 6
        else:
            rs = 6
            re = 9
        if item[0] == '1':
            ss = 0
            se = 3
        elif item[0] == '2':
            ss = 3
            se = 6
        else:
            ss = 6
            se = 9

        subg = []
        row_appender = [subg.append(num) for row in sol[ss:se] for num in row[rs:re]]

        for num in subg:
            if num != 0:
                subg_dct[num] += 1

        overallocations = ['overallocation' for val in subg_dct.values() if val > 1]
        if overallocations:
            conflicts += 1
    return conflicts


def correct_board(sol):
    for row in board:
        for num in NUMS:
            if num not in row:
                return 0
    return 1


def fix_subgrid(sol):
    pass


def fill_rows(sols):
    sol = sols[0]
    for row in sol:
        count = 0
        for n in row:
            if n == 0:
                count += 1
        if count == 1:
            zero_idx = list(row).index(0)
            for num in NUMS:
                if num not in row:
                    miss = num
                    row[zero_idx] = miss
    return np.array(sol)


def fill_cols(sol):
    board = sol[0]
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


if __name__ == '__main__':
    # Create a population
    E = Environment()

    # Register the fitness criteria (objectives) with the evo framework
    E.add_objective('blanks', blanks)
    E.add_objective('row conflicts', row_conflicts)
    E.add_objective('column conflicts', column_conflicts)
    E.add_objective('subgrid conflicts', subgrid_conflicts)
    E.add_objective('correct board', correct_board)

    # Register all the agents with the evo framework
    E.add_agent('fill rows', fill_rows, 1)
    #E.add_agent('fill columns', fill_cols, 1)
    #E.add_agent('fill miss row', fill_miss_row, 1)

    game = "431295806862017594700864320246053708108070405305140269084736002513420687607581943"
    board = create_board(game)
    E.add_solution(board)

    # Run the evolver
    E.evolve(1000000000000)

    print(E)



