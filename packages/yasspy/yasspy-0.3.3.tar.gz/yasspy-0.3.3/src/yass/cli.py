import logging

import typer

from yass.models import Board, Solver
from yass.solve import Backtrack, Dlx


app = typer.Typer()


@app.command()
def solve(
    method: str = typer.Argument(..., help="Options: 'backtrack', 'dlx'"),
    board_string: str = typer.Argument(...),
    log_level: str = typer.Option("CRITICAL", help="Log level")
):

    logging.basicConfig(level=log_level)

    solvers: dict[str, Solver] = {"backtrack": Backtrack(), "dlx": Dlx()}

    board = Board.from_string(board_string)
    print(board)
    solved_board = solvers[method].solve(board=board)
    print(solved_board)


@app.command()
def generate():
    print("Not implemented")
