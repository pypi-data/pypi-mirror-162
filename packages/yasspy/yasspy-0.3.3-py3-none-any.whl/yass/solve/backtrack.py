from typing import Iterator

from yass.models import Board, Solver


def candidate_boards(board: Board, addr: str, depth: int = 0) -> Iterator[Board]:
    candidates = board.candidates(addr)
    assert candidates is not None
    for candidate in candidates:
        board.set(addr, candidate)
        yield board
        naddr = board.next(addr)
        yield from candidate_boards(board, naddr, depth=depth + 1)
        board.unset(addr)


class Backtrack:
    def solve(self, board: Board, **kwargs) -> Board:
        """Solve a sudoku puzzle."""

        for board in candidate_boards(board, "11"):
            if board.is_completed():
                break
        return board
