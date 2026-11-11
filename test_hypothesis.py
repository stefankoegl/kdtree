#!/usr/bin/env python
""" Property-based tests for kdtree, using Hypothesis

Each test compares the kd-tree against a brute-force model (a plain list of
points) and checks structural invariants of the tree.
"""

import unittest
from collections import Counter

from hypothesis import given, settings, assume, strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine, rule, invariant, initialize, precondition,
)

import kdtree


# Integer coordinates keep distance computations exact, so results can be
# compared to the brute-force model without tolerances. A small value range
# makes duplicate points and ties (equal coordinates and distances) likely.
coord = st.integers(min_value=-20, max_value=20)
dimensions = st.integers(min_value=1, max_value=4)


def points_of(dims, min_size=0, max_size=50):
    return st.lists(st.tuples(*[coord] * dims),
                    min_size=min_size, max_size=max_size)


@st.composite
def dims_and_points(draw, min_size=1, max_size=50):
    dims = draw(dimensions)
    return dims, draw(points_of(dims, min_size, max_size))


@st.composite
def dims_points_and_query(draw, min_size=1, max_size=50):
    dims, points = draw(dims_and_points(min_size, max_size))
    query = draw(st.tuples(*[coord] * dims))
    return dims, points, query


def sq_dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def tree_points(tree):
    """ Multiset of all points stored in the tree """
    return Counter(n.data for n in tree.inorder() if n.data is not None)


def assert_strictly_valid(tc, tree):
    """ Checks the kd-tree invariant for *all* descendants of every node

    This is a brute-force counterpart to KDNode.is_valid(): every point in a
    left subtree is <= the splitting value and every point in a right subtree
    is >= it. """

    for node in tree.preorder():
        if node.data is None:
            continue
        split = node.data[node.axis]
        if node.left:
            for child in node.left.preorder():
                tc.assertLessEqual(child.data[node.axis], split)
        if node.right:
            for child in node.right.preorder():
                tc.assertGreaterEqual(child.data[node.axis], split)


class CreateProperties(unittest.TestCase):

    @given(dims_and_points())
    def test_create_preserves_points(self, dp):
        dims, points = dp
        tree = kdtree.create(points)
        self.assertEqual(tree_points(tree), Counter(points))
        self.assertEqual(tree.dimensions, dims)

    @given(dims_and_points())
    def test_create_is_valid(self, dp):
        _, points = dp
        tree = kdtree.create(points)
        self.assertTrue(tree.is_valid())
        assert_strictly_valid(self, tree)

    @given(dims_and_points())
    def test_create_is_balanced(self, dp):
        _, points = dp
        tree = kdtree.create(points)
        self.assertTrue(tree.is_balanced)

    @given(dims_and_points())
    def test_axes_cycle(self, dp):
        dims, points = dp
        tree = kdtree.create(points)
        for node in tree.preorder():
            for child, _ in node.children:
                self.assertEqual(child.axis, (node.axis + 1) % dims)

    @given(dimensions)
    def test_create_empty(self, dims):
        tree = kdtree.create(dimensions=dims)
        self.assertFalse(tree)
        self.assertEqual(tree_points(tree), Counter())


class TraversalProperties(unittest.TestCase):

    @given(dims_and_points())
    def test_traversals_agree(self, dp):
        _, points = dp
        tree = kdtree.create(points)
        expected = Counter(points)
        for traversal in (tree.inorder, tree.preorder, tree.postorder):
            self.assertEqual(Counter(n.data for n in traversal()), expected)
        self.assertEqual(Counter(n.data for n in kdtree.level_order(tree)),
                         expected)

    @given(dims_and_points())
    def test_height(self, dp):
        _, points = dp
        tree = kdtree.create(points)
        # a balanced tree built from n points has height floor(log2(n)) + 1
        self.assertEqual(tree.height(), len(points).bit_length())


class AddProperties(unittest.TestCase):

    @given(dims_and_points(min_size=0))
    def test_add_all(self, dp):
        dims, points = dp
        tree = kdtree.create(dimensions=dims)
        for n, point in enumerate(points, 1):
            node = tree.add(point)
            self.assertEqual(node.data, point)
            self.assertEqual(sum(tree_points(tree).values()), n)
        self.assertEqual(tree_points(tree), Counter(points))
        self.assertTrue(tree.is_valid())
        assert_strictly_valid(self, tree)

    @given(dims_and_points(), st.data())
    def test_add_rejects_wrong_dimensions(self, dp, data):
        dims, points = dp
        tree = kdtree.create(points)
        other_dims = data.draw(dimensions.filter(lambda d: d != dims))
        point = data.draw(st.tuples(*[coord] * other_dims))
        with self.assertRaises(ValueError):
            tree.add(point)


class RemoveProperties(unittest.TestCase):

    @given(dims_and_points(), st.randoms(use_true_random=False))
    def test_remove_all(self, dp, rnd):
        _, points = dp
        tree = kdtree.create(points)
        remaining = Counter(points)

        order = list(points)
        rnd.shuffle(order)
        for point in order:
            tree = tree.remove(point)
            remaining[point] -= 1
            self.assertEqual(tree_points(tree), +remaining)
            self.assertTrue(tree.is_valid())
            assert_strictly_valid(self, tree)

        self.assertFalse(tree)

    @given(dims_points_and_query())
    def test_remove_missing_point(self, dpq):
        _, points, query = dpq
        assume(query not in points)
        tree = kdtree.create(points)
        tree = tree.remove(query)
        self.assertEqual(tree_points(tree), Counter(points))


class SearchProperties(unittest.TestCase):

    @given(dims_points_and_query(), st.integers(min_value=1, max_value=60))
    def test_search_knn(self, dpq, k):
        _, points, query = dpq
        tree = kdtree.create(points)
        result = tree.search_knn(query, k)

        dists = [d for _, d in result]
        expected = sorted(sq_dist(p, query) for p in points)[:k]

        self.assertEqual(len(result), min(k, len(points)))
        # results are ordered by distance
        self.assertEqual(dists, sorted(dists))
        # the distances are the k smallest ones (ties may pick any node)
        self.assertEqual(dists, expected)
        for node, d in result:
            self.assertEqual(sq_dist(node.data, query), d)

        # every node is returned at most once
        self.assertEqual(len({id(node) for node, _ in result}), len(result))

    @given(dims_points_and_query(), st.integers(min_value=1, max_value=60))
    def test_search_knn_custom_dist(self, dpq, k):
        """ A custom (Manhattan) distance function yields the k nearest """
        _, points, query = dpq
        tree = kdtree.create(points)

        def manhattan(a, b, axis=None):
            if axis is not None:
                return abs(a[axis] - b[axis])
            return sum(abs(x - y) for x, y in zip(a, b))

        result = tree.search_knn(query, k, dist=manhattan)
        expected = sorted(manhattan(p, query) for p in points)[:k]
        self.assertEqual([d for _, d in result], expected)

    @given(dims_points_and_query())
    def test_search_nn(self, dpq):
        _, points, query = dpq
        tree = kdtree.create(points)
        node, d = tree.search_nn(query)
        self.assertEqual(d, min(sq_dist(p, query) for p in points))
        self.assertEqual(sq_dist(node.data, query), d)

    @given(dims_and_points(), st.data())
    def test_search_nn_finds_existing_point(self, dp, data):
        _, points = dp
        tree = kdtree.create(points)
        point = data.draw(st.sampled_from(points))
        node, d = tree.search_nn(point)
        self.assertEqual(node.data, point)
        self.assertEqual(d, 0)

    @given(dims_points_and_query(),
           st.integers(min_value=0, max_value=500))
    def test_search_nn_dist(self, dpq, distance):
        _, points, query = dpq
        tree = kdtree.create(points)
        result = tree.search_nn_dist(query, distance)
        # distances are squared and compared with a strict "<"
        expected = [p for p in points if sq_dist(p, query) < distance]
        self.assertEqual(Counter(result), Counter(expected))

    @given(dims_and_points(), st.data())
    def test_range_search(self, dp, data):
        dims, points = dp
        tree = kdtree.create(points)

        corners = data.draw(st.lists(st.tuples(coord, coord),
                                     min_size=dims, max_size=dims))
        top_left = tuple(min(a, b) for a, b in corners)
        bottom_right = tuple(max(a, b) for a, b in corners)

        result = tree.range_search(top_left, bottom_right)
        expected = [p for p in points
                    if all(lo <= x <= hi for lo, x, hi
                           in zip(top_left, p, bottom_right))]
        self.assertEqual(Counter(n.data for n in result), Counter(expected))

    @given(dims_and_points(), st.data())
    def test_range_search_invalid_rect(self, dp, data):
        dims, points = dp
        tree = kdtree.create(points)
        top_left = list(data.draw(st.tuples(*[coord] * dims)))
        bottom_right = list(top_left)
        axis = data.draw(st.integers(min_value=0, max_value=dims - 1))
        top_left[axis] = bottom_right[axis] + 1
        with self.assertRaises(ValueError):
            tree.range_search(top_left, bottom_right)

    @given(dims_and_points(min_size=0), st.data())
    def test_search_on_built_up_tree(self, dp, data):
        """ Searches also work on trees constructed by add() """
        dims, points = dp
        tree = kdtree.create(dimensions=dims)
        for p in points:
            tree.add(p)
        assume(points)
        query = data.draw(st.tuples(*[coord] * dims))
        _, d = tree.search_nn(query)
        self.assertEqual(d, min(sq_dist(p, query) for p in points))


class RebalanceProperties(unittest.TestCase):

    @given(dims_and_points())
    def test_rebalance(self, dp):
        dims, points = dp
        tree = kdtree.create(dimensions=dims)
        for p in points:
            tree.add(p)
        balanced = tree.rebalance()
        self.assertTrue(balanced.is_balanced)
        self.assertTrue(balanced.is_valid())
        assert_strictly_valid(self, balanced)
        self.assertEqual(tree_points(balanced), Counter(points))


class KDTreeMachine(RuleBasedStateMachine):
    """ Random sequences of add / remove / rebalance / search operations,
    checked against a list of points as model """

    @initialize(dims=dimensions)
    def init_tree(self, dims):
        self.dims = dims
        self.tree = kdtree.create(dimensions=dims)
        self.model = Counter()

    def point(self):
        return st.tuples(*[coord] * self.dims)

    @rule(data=st.data())
    def add(self, data):
        point = data.draw(self.point())
        self.tree.add(point)
        self.model[point] += 1

    @precondition(lambda self: self.model)
    @rule(data=st.data())
    def remove_existing(self, data):
        point = data.draw(st.sampled_from(sorted(self.model)))
        self.tree = self.tree.remove(point)
        self.model[point] -= 1
        self.model = +self.model

    @rule(data=st.data())
    def remove_any(self, data):
        point = data.draw(self.point())
        self.tree = self.tree.remove(point)
        if self.model[point]:
            self.model[point] -= 1
        self.model = +self.model

    @precondition(lambda self: self.model)
    @rule()
    def rebalance(self):
        self.tree = self.tree.rebalance()

    @precondition(lambda self: self.model)
    @rule(data=st.data(), k=st.integers(min_value=1, max_value=10))
    def search_knn(self, data, k):
        query = data.draw(self.point())
        result = self.tree.search_knn(query, k)
        expected = sorted(sq_dist(p, query)
                          for p in self.model.elements())[:k]
        assert [d for _, d in result] == expected

    @invariant()
    def same_points(self):
        assert tree_points(self.tree) == self.model

    @invariant()
    def valid(self):
        assert self.tree.is_valid()
        assert_strictly_valid(unittest.TestCase(), self.tree)


KDTreeMachine.TestCase.settings = settings(max_examples=50,
                                           stateful_step_count=30)
TestKDTreeMachine = KDTreeMachine.TestCase


if __name__ == "__main__":
    unittest.main()
