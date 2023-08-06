from yass.dlx.models import Column, Node


def uncover(col: Column):
    """Include the Column and associated rows in the search."""
    assert col.left and col.right
    cover_node = col.up
    while cover_node and cover_node != col:
        node = cover_node.left
        while isinstance(node, Node) and node and node != cover_node:
            assert node.up and node.down and node.col
            node.up.down = node
            node.down.up = node
            node.col.size += 1
            node = node.left
        cover_node = cover_node.up
    col.left.right = col
    col.right.left = col
