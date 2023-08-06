from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


BOARDS = [
    (
        "53..7...."
        "6..195..."
        ".98....6."
        "8...6...3"
        "4..8.3..1"
        "7...2...6"
        ".6....28."
        "...419..5"
        "....8..79"
    ),
]


class Solver(Protocol):
    def solve(self, board: Board, **kwargs) -> Board:
        ...


def box(col, row):
    return (col - 1) // 3 + 3 * ((row - 1) // 3) + 1


@dataclass(slots=True)
class Cell:
    col: str
    row: str
    box: str
    val: str | None = None
    og: bool = False

    def __str__(self):
        return f"{self.val or '.'}"

    def with_val(self, val: str) -> Cell:
        if self.is_set():
            raise ValueError(
                f"(col={self.col}, row={self.row}) is set, not setting to {val}"
            )
        return Cell(col=self.col, row=self.row, box=self.box, val=val, og=self.og)

    def neighbour(self, c: Cell) -> bool:
        if self.col == c.col and self.row == c.row and self.box == c.box:
            return False
        return (self.col == c.col) or (self.row == c.row) or (self.box == c.box)

    def is_set(self):
        return self.val is not None

    def can_unset(self):
        return not self.og


class InvalidBoard(Exception):
    """"""


def invalid_board(string: str):
    err = {}
    if not len(string) == 81:
        err["msg"] = "Incorrect number of cells"
    return err


class Board:
    """Sudoku board."""

    SIZE = 9
    OPTIONS = "123456789"

    @classmethod
    def from_string(cls, string: str) -> Board:
        board = cls()
        if err := invalid_board(string):
            raise InvalidBoard(err["msg"])
        for addr, val in zip(board, string):
            if val != ".":
                board.set(addr, val)
                board[addr].og = True
        return board

    def __init__(self):
        self._set_count = 0
        self._cells = {
            f"{col}{row}": Cell(
                col=str(col),
                row=str(row),
                box=str(box(col, row)),
            )
            for row in range(1, self.SIZE + 1)
            for col in range(1, self.SIZE + 1)
        }
        self._neighbours = {
            f"{col}{row}": [
                c for _, c in self.items() if c.neighbour(self[f"{col}{row}"])
            ]
            for row in range(1, self.SIZE + 1)
            for col in range(1, self.SIZE + 1)
        }

    def __iter__(self):
        return iter(self._cells)

    def __getitem__(self, k) -> Cell:
        return self._cells[k]

    def __str__(self):
        s = ""
        for row in range(1, self.SIZE + 1):
            for col in range(1, self.SIZE + 1):
                s += str(self[f"{col}{row}"])
                if col in [3, 6]:
                    s += "|"
            s += "\n"
            if row in [3, 6]:
                s += "---|---|---\n"
        return s

    def items(self):
        return self._cells.items()

    def neighbour_vals(self, addr):
        return set(c.val for c in self._neighbours[addr] if c.is_set())

    def candidates(self, addr: str) -> str | None:
        if self[addr].is_set():
            return self[addr].val
        return "".join(set(self.OPTIONS) - self.neighbour_vals(addr))

    def next(self, addr: str) -> str:
        col, row = [int(x) for x in addr]
        if col < self.SIZE:
            return f"{col + 1}{row}"
        return f"1{row + 1}"

    def set(self, addr: str, val: str) -> None:
        if not self[addr].is_set():
            self._set_count += 1
            self[addr].val = val

    def unset(self, addr: str) -> None:
        if self[addr].can_unset():
            self._set_count -= 1
            self[addr].val = None

    def is_completed(self) -> bool:
        return self._set_count == 81
