#!/usr/bin/env python

from __future__ import absolute_import

import sys
import random
import logging
import unittest
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


    def test_add(self, num=10):
        """ Tests random additions to a tree, multiple times """

        for i in range(num):
            self.do_random_add()


    def do_random_add(self, num_points=100):

        points = list(set(islice(random_points(), 0, num_points)))
        tree = kdtree.KDNode()
        for n, point in enumerate(points, 1):

            tree.add(point)

            self.assertTrue(tree.is_valid())

            self.assertTrue(point in [node.data for node in tree.inorder()])

            nodes_in_tree = len(list(tree.inorder()))
            self.assertEqual(nodes_in_tree, n)


def random_tree(nodes=20, dimensions=3, minval=0, maxval=100):
    points = list(islice(random_points(), 0, nodes))
    tree = kdtree.create(points)
    return tree

def random_point(dimensions, minval, maxval):
    return tuple(random.randint(minval, maxval) for _ in range(dimensions))

def random_points(dimensions=3, minval=0, maxval=100):
    while True:
        yield random_point(dimensions, minval, maxval)


if __name__ == '__main__':

    if coverage is not None:
        coverage.erase()
        coverage.start()

    suite = unittest.TestLoader().loadTestsFromTestCase(RemoveTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        sys.exit(1)

    if coverage is not None:
        coverage.stop()
        coverage.report([kdtree])
        coverage.erase()
