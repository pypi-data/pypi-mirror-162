from yass.dlx.models import Column, Node


def cover(col: Column):
    """Exclude the Column and associated rows from the search."""
    assert col.left and col.right
    col.left.right = col.right
    col.right.left = col.left
    if col.down == col:
        return
    cover_node = col.down
    while cover_node and cover_node != col:
        node = cover_node.right
        while isinstance(node, Node) and node and node != cover_node:
            assert node.up and node.down and node.col
            node.up.down = node.down
            node.down.up = node.up
            node.col.size -= 1
            node = node.right
        cover_node = cover_node.down
