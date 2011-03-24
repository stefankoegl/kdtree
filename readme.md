A simple kd-tree in Python
==========================

The kdtree package can construct, modify and search
[kd-trees]{http://en.wikipedia.org/wiki/Kd-tree}.

Usage
-----

    >>> import kdtree

    >>> points = [(2,3), (5,4), (9,6), (4,7), (8,1), (7,2)]
    >>> tree = kdtree.create(points)
    >>> tree
    <Node at (7, 2)>

    >>> # add points
    >>> tree.add( (10, 2) )
    >>> tree.add( (1, 15) )

    >>> # traverse the tree in in-, pre- and postorder
    >>> tree.inorder()
    [(2, 3), (5, 4), (1, 15), (4, 7), (7, 2), (8, 1), (10, 2), (9, 6)]

    >>> # find the nearest node to a point
    >>> p = tree.search_nn( (5, 5) )
    >>> p
    <Node at (5, 4)>

    >>> # every node represents its subtree
    >>> p.postorder()
    [(2, 3), (1, 15), (4, 7), (5, 4)]
    >>> p.search_nn( (1, 2) )
    <Node at (2, 3)>

