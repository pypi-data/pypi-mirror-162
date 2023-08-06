from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence


@dataclass
class Node:

    row_idx: int
    col: Column
    left: Node | None = None
    right: Node | None = None
    up: Node | Column | None = None
    down: Node | Column | None = None


@dataclass
class Column:

    name: str
    left: Column | None = None
    right: Column | None = None
    up: Node | Column | None = None
    down: Node | Column | None = None
    size: int = 0


def choose_column(root: Column) -> Column:
    """Choose the next Column object to cover."""
    col = root.right
    min_col = root

    min_size = 1_000_000_000
    while col and col != root:
        s = col.size
        if s < min_size:
            min_col = col
            min_size = s
        col = col.right
    return min_col


def from_matrix(
    matrix: Sequence[Sequence[int]],
    column_names: Sequence[str] | None = None,
) -> Column:
    """Build a Problem object from a sequence of rows."""

    root = Column("__root__")

    cols: list[Column] = []
    if column_names is None:
        ncols: Sequence[str] = [str(i) for i in range(len(matrix[0]))]
    else:
        ncols = column_names

    for i, row in enumerate(matrix):
        if i == 1:
            cols[0].left = root
            cols[-1].right = root
            root.left = cols[-1]
            root.right = cols[0]
        row_nodes: list[Node] = []
        for j, elem in enumerate(row):
            if i == 0:
                col = Column(name=ncols[j])
                if cols:
                    col.left = cols[-1]
                    cols[-1].right = col
                cols.append(col)
            if elem:
                node = Node(
                    row_idx=i,
                    col=cols[j],
                )
                cols[j].size += 1
                up: Node | Column = node.col
                while up.down:
                    up = up.down
                node.up = up
                up.down = node
                if row_nodes:
                    node.left = row_nodes[-1]
                    row_nodes[-1].right = node
                row_nodes.append(node)
        row_nodes[0].left = row_nodes[-1]
        row_nodes[-1].right = row_nodes[0]

    # point all the bottom nodes back to the top nodes and vice versa
    for col in cols:
        bottom = col.down
        while bottom and bottom.down:
            bottom = bottom.down
        assert bottom
        bottom.down = col
        col.up = bottom

    return root
