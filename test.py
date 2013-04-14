#!/usr/bin/env python

from __future__ import absolute_import

import sys
import random
import logging
import unittest
import doctest
from itertools import islice

import kdtree


try:
    import coverage
except ImportError:
    coverage = None


class RemoveTest(unittest.TestCase):


    def test_remove(self, num=100):
        """ Tests random removal from a tree, multiple times """

        for i in range(num):
            self.do_random_remove()


    def do_random_remove(self):
        """ Creates a random tree, removes all points in random order """

        points = list(set(islice(random_points(), 0, 20)))
        tree =  kdtree.create(points)
        self.assertTrue(tree.is_valid())

        random.shuffle(points)
        while points:
            point = points.pop(0)

            tree = tree.remove(point)

            # Check if the Tree is valid after the removal
            self.assertTrue(tree.is_valid())

            # Check if the point has actually been removed
            self.assertTrue(point not in [n.data for n in tree.inorder()])

            # Check if the removal reduced the number of nodes by 1 (not more, not less)
            remaining_points = len(points)
            nodes_in_tree = len(list(tree.inorder()))
            self.assertEqual(nodes_in_tree, remaining_points)

    def test_remove_empty_tree(self):
        tree = kdtree.create(dimensions=2)
        tree.remove( (1, 2) )
        self.assertFalse(bool(tree))


class AddTest(unittest.TestCase):

    def test_add(self, num=10):
        """ Tests random additions to a tree, multiple times """

        for i in range(num):
            self.do_random_add()


    def do_random_add(self, num_points=100):

        points = list(set(islice(random_points(), 0, num_points)))
        tree = kdtree.create(dimensions=len(points[0]))
        for n, point in enumerate(points, 1):

            tree.add(point)

            self.assertTrue(tree.is_valid())

            self.assertTrue(point in [node.data for node in tree.inorder()])

            nodes_in_tree = len(list(tree.inorder()))
            self.assertEqual(nodes_in_tree, n)


class InvalidTreeTests(unittest.TestCase):


    def test_invalid_child(self):
        """ Children on wrong subtree invalidate Tree """
        child = kdtree.KDNode( (3, 2) )
        child.axis = 2
        tree = kdtree.create([(2, 3)])
        tree.left=child
        self.assertFalse(tree.is_valid())

        tree = kdtree.create([(4, 1)])
        tree.right=child
        self.assertFalse(tree.is_valid())


    def test_different_dimensions(self):
        """ Can't create Tree for Points of different dimensions """
        points = [ (1, 2), (2, 3, 4) ]
        self.assertRaises(ValueError, kdtree.create, points)


class TreeTraversals(unittest.TestCase):

    def test_same_length(self):
        tree = random_tree()

        inorder_len = len(list(tree.inorder()))
        preorder_len = len(list(tree.preorder()))
        postorder_len = len(list(tree.postorder()))

        self.assertEqual(inorder_len, preorder_len)
        self.assertEqual(preorder_len, postorder_len)



class BalanceTests(unittest.TestCase):


    def test_rebalance(self):

        tree = random_tree(1)
        while tree.is_balanced:
            tree.add(random_point())

        tree = tree.rebalance()
        self.assertTrue(tree.is_balanced)



class NearestNeighbor(unittest.TestCase):

    def test_search_nn(self, nodes=100):

        points = list(islice(random_points(), 0, nodes))
        tree = kdtree.create(points)

        point = random_point()
        nn = tree.search_nn(point)

        best = None
        best_dist = None
        for p in tree.inorder():
            dist = p.dist(point)
            if best is None or dist < best_dist:
                best = p
                best_dist = dist

        self.assertEqual(best_dist, best.dist(point))



def random_tree(nodes=20, dimensions=3, minval=0, maxval=100):
    points = list(islice(random_points(), 0, nodes))
    tree = kdtree.create(points)
    return tree

def random_point(dimensions=3, minval=0, maxval=100):
    return tuple(random.randint(minval, maxval) for _ in range(dimensions))

def random_points(dimensions=3, minval=0, maxval=100):
    while True:
        yield random_point(dimensions, minval, maxval)


if __name__ == '__main__':

    if coverage is not None:
        coverage.erase()
        coverage.start()

    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    suite.addTest(doctest.DocTestSuite(kdtree))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        sys.exit(1)

    if coverage is not None:
        coverage.stop()
        coverage.report([kdtree])
        coverage.erase()
