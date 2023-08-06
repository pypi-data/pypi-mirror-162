import argparse
import logging

from yass.models import Board, Solver
from yass.solve import Backtrack, Dlx


parser = argparse.ArgumentParser()
parser.add_argument("method")
parser.add_argument("board_string")
parser.add_argument("--log_level", default="CRITICAL")


def cli():
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    solvers: dict[str, Solver] = {"backtrack": Backtrack(), "dlx": Dlx()}

    board = Board.from_string(args.board_string)
    print(board)
    solved_board = solvers[args.method].solve(board=board)
    print(solved_board)


if __name__ == "__main__":
    cli()
