""" Example usage of kdtree whose types are checked against kdtree.pyi

The expected types are given as strings, because the classes in kdtree.py are
not subscriptable at runtime (generics only exist in the stubs).

This file is executed by test_typing.py (so it has to work at runtime) and
type-checked with mypy and pyright (so the stubs have to describe the runtime
behaviour correctly). """

from __future__ import annotations

import collections
import decimal
from typing import Any, Iterator, List, Optional, Tuple, assert_type

import kdtree


class Item(object):
    """ A point carrying a payload (see readme) """

    def __init__(self, x: float, y: float, data: str) -> None:
        self.coords = (x, y)
        self.data = data

    def __len__(self) -> int:
        return len(self.coords)

    def __getitem__(self, i: int) -> float:
        return self.coords[i]


def manhattan(a: Any, b: Any, axis: Optional[int] = None) -> int:
    axes = range(len(a)) if axis is None else [axis]
    return sum(abs(a[i] - b[i]) for i in axes)


def check_create() -> None:
    tree = kdtree.create([(1, 2), (3, 4), (5, 6)])
    assert_type(tree, 'kdtree.KDNode[Tuple[int, int]]')

    empty = kdtree.create(dimensions=2)
    assert_type(empty, 'kdtree.KDNode[Any]')
    assert not empty

    empty2 = kdtree.create(None, 2)
    assert_type(empty2, 'kdtree.KDNode[Any]')

    custom_axis = kdtree.create([(1, 2), (3, 4)], axis=1,
                                sel_axis=lambda axis: 1 - axis)
    assert custom_axis.axis == 1

    items = kdtree.create([Item(2, 3, 'First'), Item(3, 4, 'Second')])
    assert_type(items, 'kdtree.KDNode[Item]')
    assert items.data is not None
    assert_type(items.data.data, 'str')


def check_node_attributes() -> None:
    tree = kdtree.create([(1, 2), (3, 4), (5, 6)])

    assert_type(tree.data, 'Optional[Tuple[int, int]]')
    assert_type(tree.left, 'Optional[kdtree.KDNode[Tuple[int, int]]]')
    assert_type(tree.right, 'Optional[kdtree.KDNode[Tuple[int, int]]]')
    assert_type(tree.axis, 'Optional[int]')
    assert_type(tree.dimensions, 'Optional[int]')
    assert_type(tree.is_leaf, 'bool')
    assert_type(tree.is_balanced, 'bool')
    assert_type(tree.height(), 'int')
    assert_type(tree.is_valid(), 'bool')
    assert_type(bool(tree), 'bool')

    for child, pos in tree.children:
        assert_type(child, 'kdtree.KDNode[Tuple[int, int]]')
        assert_type(pos, 'int')
        assert tree.get_child_pos(child) == pos

    # detach and re-attach a subtree
    subtree = tree.right
    tree.right = None
    tree.set_child(1, subtree)
    assert tree.right is subtree


def check_traversal() -> None:
    tree = kdtree.create([(1, 2), (3, 4), (5, 6)])

    assert_type(tree.inorder(), 'Iterator[kdtree.KDNode[Tuple[int, int]]]')
    assert_type(tree.preorder(), 'Iterator[kdtree.KDNode[Tuple[int, int]]]')
    assert_type(tree.postorder(), 'Iterator[kdtree.KDNode[Tuple[int, int]]]')

    nodes = list(kdtree.level_order(tree))
    assert_type(nodes, 'List[kdtree.KDNode[Tuple[int, int]]]')
    assert len(nodes) == 3

    plain = kdtree.Node(1, left=kdtree.Node(2))
    assert_type(plain, 'kdtree.Node[int]')
    assert_type(plain.data, 'Optional[int]')
    assert [n.data for n in plain.inorder()] == [2, 1]


def check_modification() -> None:
    tree = kdtree.create([(1, 2), (3, 4), (5, 6)])

    added = tree.add((7, 8))
    assert_type(added, 'kdtree.KDNode[Tuple[int, int]]')
    assert added.data == (7, 8)

    new_root = tree.remove((7, 8))
    assert_type(new_root, 'kdtree.KDNode[Tuple[int, int]]')

    # removing from an empty tree returns the (empty) tree
    empty = kdtree.create(dimensions=2)
    assert empty.remove((1, 2)) is empty

    rebalanced = new_root.rebalance()
    assert_type(rebalanced, 'kdtree.KDNode[Tuple[int, int]]')
    assert rebalanced.is_balanced

    # creates an empty child node
    empty_child = tree.create_subnode(None)
    assert_type(empty_child, 'kdtree.KDNode[Tuple[int, int]]')
    assert not empty_child

    # a single node has no replacement
    replacement, parent = kdtree.create([(1, 2)]).find_replacement()
    assert_type(replacement, 'Optional[kdtree.KDNode[Tuple[int, int]]]')
    assert_type(parent, 'kdtree.KDNode[Tuple[int, int]]')
    assert replacement is None


def check_search() -> None:
    tree = kdtree.create([(1, 2), (3, 4), (5, 6)])

    node, dist = tree.search_nn((1, 1))
    assert_type(node, 'kdtree.KDNode[Tuple[int, int]]')
    assert_type(dist, 'float')
    assert node.data == (1, 2)

    node2, dist2 = tree.search_nn((1, 1), dist=manhattan)
    assert_type(dist2, 'int')
    assert dist2 == 1

    knn = tree.search_knn((1, 1), 2)
    assert_type(knn, 'List[Tuple[kdtree.KDNode[Tuple[int, int]], float]]')
    assert len(knn) == 2

    knn_custom = tree.search_knn((1, 1), 2, dist=manhattan)
    assert_type(knn_custom, 'List[Tuple[kdtree.KDNode[Tuple[int, int]], int]]')

    knn_lambda = tree.search_knn((1, 1), 1,
                                 dist=lambda a, b, axis=None: manhattan(a, b, axis))
    assert len(knn_lambda) == 1

    # any negatable and comparable type can be used as a distance
    def decimal_dist(a: Any, b: Any, axis: Optional[int] = None) -> decimal.Decimal:
        return decimal.Decimal(manhattan(a, b, axis))

    node3, dist3 = tree.search_nn((1, 1), dist=decimal_dist)
    assert_type(dist3, 'decimal.Decimal')
    assert dist3 == 1

    # axis is always passed as keyword, so it may be keyword-only
    def kw_only_dist(a: Any, b: Any, *, axis: Optional[int]) -> int:
        return manhattan(a, b, axis)

    node4, dist4 = tree.search_nn((1, 1), dist=kw_only_dist)
    assert_type(dist4, 'int')
    assert dist4 == 1

    # distance functions can be typed for the stored and the query points
    items = kdtree.create([Item(2, 3, 'First'), Item(3, 4, 'Second')])

    def item_dist(a: Item, b: Tuple[float, float], *,
                  axis: Optional[int]) -> float:
        return manhattan(a.coords, b, axis)

    item_node, item_d = items.search_nn((1.0, 2.0), dist=item_dist)
    assert_type(item_node, 'kdtree.KDNode[Item]')
    assert_type(item_d, 'float')
    assert item_node.data is not None and item_node.data.data == 'First'

    within = tree.search_nn_dist((1, 1), 20)
    assert_type(within, 'List[Tuple[int, int]]')
    assert sorted(within) == [(1, 2), (3, 4)]

    in_range = tree.range_search((0, 0), (4, 4))
    assert_type(in_range, 'List[kdtree.KDNode[Tuple[int, int]]]')
    assert len(in_range) == 2

    assert_type(tree.dist((0, 0)), 'float')
    assert_type(tree.axis_dist((0, 0), 0), 'float')


def check_mixed_point_types() -> None:
    Point = collections.namedtuple('Point', 'x y z')
    tree = kdtree.create([(2, 3, 4), [4, 5, 6], Point(5, 3, 2)])
    res, dist = tree.search_nn((1, 2, 3))
    assert res == kdtree.KDNode((2, 3, 4))


def check_misc() -> None:
    assert_type(kdtree.__version__, 'str')
    assert_type(kdtree.check_dimensionality([(1, 2), (3, 4)]), 'int')
    assert kdtree.check_dimensionality({(1, 2), (3, 4)}, dimensions=2) == 2


def check_unordered_points() -> None:
    # sets of points can be used if the dimensions are given
    tree = kdtree.create({(1, 2), (3, 4)}, dimensions=2)
    assert_type(tree, 'kdtree.KDNode[Tuple[int, int]]')
    assert tree.is_valid()


def main() -> None:
    check_create()
    check_node_attributes()
    check_traversal()
    check_modification()
    check_search()
    check_mixed_point_types()
    check_misc()
    check_unordered_points()


if __name__ == '__main__':
    main()
