from typing import Sequence

from yass.dlx.models import Column, from_matrix
from yass.dlx.search import search
from yass.models import Board, Cell


def from_board(
    board: Board,
) -> tuple[Column, Sequence[Sequence[int]], tuple[str, ...]]:
    matrix, column_names = remove_empty_cols(*to_matrix(board))
    return (
        from_matrix(matrix=matrix, column_names=column_names),
        matrix,
        column_names,
    )


def cell_to_idx() -> dict[str, int]:
    mapper = {}
    i = 0
    for c in "PRCB":
        for x in range(1, 10):
            for y in range(1, 10):
                mapper[f"{c}{x}{y}"] = i
                i += 1
    return mapper


def cell_to_row(
    cell: Cell, cell_to_idx_mapper: dict[str, int], row_len: int
) -> tuple[int, ...]:
    row = [0] * row_len
    row[cell_to_idx_mapper[f"P{cell.row}{cell.col}"]] = 1
    row[cell_to_idx_mapper[f"R{cell.val}{cell.row}"]] = 1
    row[cell_to_idx_mapper[f"C{cell.val}{cell.col}"]] = 1
    row[cell_to_idx_mapper[f"B{cell.val}{cell.box}"]] = 1
    return tuple(row)


def to_matrix(board: Board) -> tuple[Sequence[Sequence[int]], tuple[str, ...]]:
    cell_to_idx_mapper = cell_to_idx()
    row_len = len(cell_to_idx_mapper)
    rows = []
    for addr, cell in board.items():
        if cell.is_set():
            rows.append(cell_to_row(cell, cell_to_idx_mapper, row_len))
        else:
            candidates = board.candidates(addr)
            assert candidates
            for val in candidates:
                rows.append(
                    cell_to_row(board[addr].with_val(val), cell_to_idx_mapper, row_len)
                )
    return tuple(rows), tuple(cell_to_idx_mapper)


def remove_empty_cols(
    matrix: Sequence[Sequence[int]], col_names: tuple[str, ...]
) -> tuple[Sequence[Sequence[int]], tuple[str, ...]]:
    tr = list(map(list, zip(*matrix)))
    tr_new = []
    col_names_new = []
    for col, col_name in zip(tr, col_names):
        if any(col):
            tr_new.append(col)
            col_names_new.append(col_name)
    return tuple(map(list, zip(*tr_new))), tuple(col_names_new)


def populate_board(
    board: Board, matrix: Sequence[Sequence[int]], col_names: tuple[str, ...]
) -> Board:

    for row in matrix:
        addr_found = False
        for col, name in zip(row, col_names):
            if col:
                if not addr_found:
                    r, c = list(name[1:])  # Remove P
                    addr = f"{c}{r}"  # board addresses are col, row
                    addr_found = True
                else:
                    val = name[1]  # {R,C,B}<val><row,col,box idx>
        board.set(addr, val)
    return board


class Dlx:
    def solve(self, board: Board, **kwargs) -> Board:
        """Solve a sudoku puzzle."""

        col, m, c = from_board(board)
        soln = search(col, soln_length=81)
        soln_matrix = [x for i, x in enumerate(m) if i in soln]
        return populate_board(board=board, matrix=soln_matrix, col_names=c)
