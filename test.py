#!/usr/bin/env python

from __future__ import absolute_import

import sys
import random
import logging
import unittest
import doctest
import collections
from itertools import islice

# import after starting coverage, to ensure that import-time code is covered
import kdtree

class RemoveTest(unittest.TestCase):


    def test_remove_duplicates(self):
        """ creates a tree with only duplicate points, and removes them all """

        points = [(1,1)] * 100
        tree = kdtree.create(points)
        self.assertTrue(tree.is_valid())

        random.shuffle(points)
        while points:
            point = points.pop(0)

            tree = tree.remove(point)

            # Check if the Tree is valid after the removal
            self.assertTrue(tree.is_valid())

            # Check if the removal reduced the number of nodes by 1 (not more, not less)
            remaining_points = len(points)
            nodes_in_tree = len(list(tree.inorder()))
            self.assertEqual(nodes_in_tree, remaining_points)


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

    def test_search_knn(self):
        points = [(50, 20), (51, 19), (1, 80)]
        tree = kdtree.create(points)
        point = (48, 18)

        all_dist = []
        for p in tree.inorder():
            dist = p.dist(point)
            all_dist.append([p, dist])

        all_dist = sorted(all_dist, key = lambda n:n[1])

        result = tree.search_knn(point, 1)
        self.assertEqual(result[0][1], all_dist[0][1])

        result = tree.search_knn(point, 2)
        self.assertEqual(result[0][1], all_dist[0][1])
        self.assertEqual(result[1][1], all_dist[1][1])

        result = tree.search_knn(point, 3)
        self.assertEqual(result[0][1], all_dist[0][1])
        self.assertEqual(result[1][1], all_dist[1][1])
        self.assertEqual(result[2][1], all_dist[2][1])

    def test_search_nn(self, nodes=100):
        points = list(islice(random_points(), 0, nodes))
        tree = kdtree.create(points)
        point = random_point()

        nn, dist = tree.search_nn(point)
        best, best_dist = self.find_best(tree, point)
        self.assertEqual(best_dist, dist, msg=', '.join(repr(p) for p in points) + ' / ' + repr(point))


    def test_search_nn2(self):
        points = [(1,2,3),(5,1,2),(9,3,4),(3,9,1),(4,8,3),(9,1,1),(5,0,0),
                  (1,1,1),(7,2,2),(5,9,1),(1,1,9),(9,8,7),(2,3,4),(4,5,4.01)]
        tree = kdtree.create(points)
        point = (2,5,6)

        nn, dist = tree.search_nn(point)
        best, best_dist = self.find_best(tree, point)
        self.assertEqual(best_dist, dist)


    def test_search_nn3(self):
        points = [(0, 25, 73), (1, 91, 85), (1, 47, 12), (2, 90, 20),
      (2, 66, 79), (2, 46, 27), (4, 48, 99), (5, 73, 64), (7, 42, 70),
      (7, 34, 60), (8, 86, 80), (10, 27, 14), (15, 64, 39), (17, 74, 24),
      (18, 58, 12), (18, 58, 5), (19, 14, 2), (20, 88, 11), (20, 28, 58),
      (20, 79, 48), (21, 32, 8), (21, 46, 41), (22, 6, 4), (22, 42, 68),
      (22, 62, 42), (24, 70, 96), (27, 77, 57), (27, 47, 39), (28, 61, 19),
      (30, 28, 22), (34, 13, 85), (34, 39, 96), (34, 90, 32), (39, 7, 45),
      (40, 61, 53), (40, 69, 50), (41, 45, 16), (41, 15, 44), (42, 40, 19),
      (45, 6, 68), (46, 79, 91), (47, 91, 86), (47, 50, 24), (48, 57, 64),
      (49, 21, 72), (49, 87, 21), (49, 41, 62), (54, 94, 32), (56, 14, 54),
      (56, 93, 2), (58, 34, 44), (58, 27, 42), (59, 62, 80), (60, 69, 69),
      (61, 67, 35), (62, 31, 50), (63, 9, 93), (63, 46, 95), (64, 31, 2),
      (64, 2, 36), (65, 23, 96), (66, 94, 69), (67, 98, 10), (67, 40, 88),
      (68, 4, 15), (68, 1, 6), (68, 88, 72), (70, 24, 53), (70, 31, 87),
      (71, 95, 26), (74, 80, 34), (75, 59, 99), (75, 15, 25), (76, 90, 99),
      (77, 75, 19), (77, 68, 26), (80, 19, 98), (82, 90, 50), (82, 87, 37),
      (84, 88, 59), (85, 76, 61), (85, 89, 20), (85, 64, 64), (86, 55, 92),
      (86, 15, 69), (87, 48, 46), (87, 67, 47), (89, 81, 65), (89, 87, 39),
      (89, 87, 3), (91, 65, 87), (94, 37, 74), (94, 20, 92), (95, 95, 49),
      (96, 15, 80), (96, 27, 39), (97, 87, 32), (97, 43, 7), (98, 78, 10),
      (99, 64, 55)]

        tree = kdtree.create(points)
        point = (66, 54, 29)

        nn, dist = tree.search_nn(point)
        best, best_dist = self.find_best(tree, point)
        self.assertEqual(best_dist, dist)



    def find_best(self, tree, point):
        best = None
        best_dist = None
        for p in tree.inorder():
            dist = p.dist(point)
            if best is None or dist < best_dist:
                best = p
                best_dist = dist
        return best, best_dist

    def test_search_nn_dist(self):
        """ tests search_nn_dist() according to bug #8 """

        points = [(x,y) for x in range(10) for y in range(10)]
        tree = kdtree.create(points)
        nn = tree.search_nn_dist((5,5), 2.5)

        self.assertEqual(len(nn), 9)
        self.assertTrue( (4,4) in nn)
        self.assertTrue( (4,5) in nn)
        self.assertTrue( (4,6) in nn)
        self.assertTrue( (5,4) in nn)
        self.assertTrue( (6,4) in nn)
        self.assertTrue( (6,6) in nn)
        self.assertTrue( (5,5) in nn)
        self.assertTrue( (5,6) in nn)
        self.assertTrue( (6,5) in nn)

    def test_search_nn_dist2(self):
        """ Test case from #36 """
        points = [[0.25, 0.25, 1.600000023841858], [0.75, 0.25, 1.600000023841858], [1.25, 0.25, 1.600000023841858],
               [1.75, 0.25, 1.600000023841858], [2.25, 0.25, 1.600000023841858], [2.75, 0.25, 1.600000023841858]]

        expected = [0.25, 0.25, 1.600000023841858]
        tree = kdtree.create(points)
        rmax = 1.0
        search_p = [0.42621034383773804, 0.18793821334838867, 1.44510018825531]
        results = tree.search_nn_dist(search_p, rmax)
        found = False
        for result in results:
            if result == expected:
                found = True
                break
        self.assertTrue(found)

    def test_search_nn_dist3(self):
        """ Test case from #36 """
        pointslst = [
            (0.25, 0.25, 1.600000023841858),
            (0.75, 0.25, 1.600000023841858),
            (1.25, 0.25, 1.600000023841858),
            (1.75, 0.25, 1.600000023841858),
            (2.25, 0.25, 1.600000023841858),
            (2.75, 0.25, 1.600000023841858),
        ]

        tree = kdtree.create(pointslst)
        point = (0.42621034383773804, 0.18793821334838867, 1.44510018825531)

        points = tree.inorder()
        points = sorted(points, key=lambda p: p.dist(point))

        for p in points:
            dist = p.dist(point)
            nn = tree.search_nn_dist(point, dist)

            for pn in points:
                if pn in nn:
                    msg = '{} in {} but {} < {}'.format(
                        pn, nn, pn.dist(point), dist)
                    self.assertTrue(pn.dist(point) < dist, msg)
                else:
                    msg = '{} not in {} but {} >= {}'.format(
                        pn, nn, pn.dist(point), dist)
                    self.assertTrue(pn.dist(point) >= dist, msg)

    def test_search_nn_dist_random(self):

        for n in range(50):
            tree = random_tree()
            point = random_point()
            points = tree.inorder()

            points = sorted(points, key=lambda p: p.dist(point))

            for p in points:
                dist = p.dist(point)
                nn = tree.search_nn_dist(point, dist)

                for pn in points:
                    if pn in nn:
                        self.assertTrue(pn.dist(point) < dist, '%s in %s but %s < %s' % (pn, nn, pn.dist(point), dist))
                    else:
                        self.assertTrue(pn.dist(point) >= dist, '%s not in %s but %s >= %s' % (pn, nn, pn.dist(point), dist))


class PointTypeTests(unittest.TestCase):
    """ test using different types as points """

    def test_point_types(self):
        emptyTree = kdtree.create(dimensions=3)
        point1 = (2, 3, 4)
        point2 = [4, 5, 6]
        Point = collections.namedtuple('Point', 'x y z')
        point3 = Point(5, 3, 2)
        tree = kdtree.create([point1, point2, point3])
        res, dist = tree.search_nn( (1, 2, 3) )

        self.assertEqual(res, kdtree.KDNode( (2, 3, 4) ))


class PayloadTests(unittest.TestCase):
    """ test tree.add() with payload """

    def test_payload(self, nodes=100, dimensions=3):
        points = list(islice(random_points(dimensions=dimensions), 0, nodes))
        tree = kdtree.create(dimensions=dimensions)

        for i, p in enumerate(points):
            tree.add(p).payload = i

        for i, p in enumerate(points):
            self.assertEqual(i, tree.search_nn(p)[0].payload)

class RangeTests(unittest.TestCase):
    """ test range_search"""

    def test_2drange(self):
        top_left = (-9, 4)
        bottom_right = (13, 20)

        points = [(6, 16), (11, 10), (-29, -7), (7, -16), (22, 21), (-7, 0), (2, -26), (-30, -20), (-12, -26), (-28, 18), (-20, -29), (-12, 26), (15, -3), (17, 20), (26, 19), (19, -28), (-7, 16), (22, 23), (13, -3), (-18, -10), (3, -18), (-18, 3), (21, -14), (-1, -1), (29, 25), (17, -12), (-13, -20), (11, 19), (21, 26), (-11, -11), (-18, -8), (5, 18), (27, 6), (1, 12), (-3, 25), (6, -7), (-28, -2), (-1, -15), (2, -11), (15, -16), (12, 14), (-9, 4), (-8, -25), (28, -29), (12, 3), (27, 19), (-13, -12), (22, 20), (-22, 12), (-1, 3), (4, 10), (-21, 10), (-25, 22), (7, -9), (-26, -25), (-9, 14), (17, 12), (23, 22), (-4, 4), (24, 10), (23, -20), (-9, -11), (-3, -6), (-7, -5), (-21, -22), (1, -8), (-7, 8), (10, -20), (-22, 11), (3, -6), (-29, 17), (-7, 3), (12, -17), (-26, 21), (21, -4), (13, 15), (-23, -8), (10, -3), (15, 27), (5, -4), (22, -20), (-12, -29), (16, 8), (-4, -27), (23, 14), (23, -4), (2, 29), (5, -9), (-15, -3), (-10, 29), (24, 27), (-28, -11), (-17, -30), (20, 25), (8, -20), (-20, 6), (3, 0), (-26, -9), (16, -29), (29, 6), (-27, -9), (-7, 17), (2, 9), (-30, 6), (-1, -28), (27, 5), (-27, 20), (0, -20), (15, 6), (-21, -22), (-22, -12), (18, -30), (14, 4), (10, -13), (-26, -29), (-7, 7), (23, -7), (25, -24), (5, 2), (-13, -5), (10, 18), (-2, 26), (23, -22), (-2, -11), (-7, -23), (24, 19), (4, 27), (-15, -30), (-4, -16), (-20, -7), (22, 28), (-9, -6), (-12, 29), (6, -30), (25, 1), (12, -20), (4, 28), (-25, 12), (-22, -28), (0, -20), (14, -6), (17, 29), (4, -22), (16, -28), (15, -11), (6, -19), (-11, -16), (-19, 18), (5, 4), (22, -2), (18, 1), (25, 22), (17, 21), (-28, -2), (9, -12), (-11, 27), (-29, -25), (-16, -7), (-18, 1), (3, -2), (-25, -28), (19, -20), (-24, 6), (-12, 26), (22, 6), (-17, 25), (-6, 16), (-12, -8), (-4, 10), (12, -1), (18, 15), (-28, -15), (22, -15), (-13, -24), (-11, 15), (9, -24), (1, 3), (-13, 6), (24, 24), (-6, -23), (-21, 16), (-21, -4), (21, 4), (0, 25), (13, 25), (-12, 5), (28, -11), (-23, -28), (8, 2), (-6, -10), (11, 11), (-5, 25), (17, -11), (-19, 7), (-5, -9), (-28, 3), (9, 25), (-21, 4), (-9, -5), (28, -3)]

        known_range = []
        for (x, y) in points:
            if (x >= top_left[0]) and (x <= bottom_right[0]) and (y >= top_left[1]) and (y <= bottom_right[1]):
                known_range.append((x, y))
        known_range.sort()

        tree = kdtree.create(points)
        tree.rebalance()

        unknown_range = [x.data for x in tree.range_search(top_left, bottom_right)]
        unknown_range.sort()

        self.assertEqual(known_range, unknown_range)

    def test_3drange(self):
        top_left = (-18, -15, 10)
        bottom_right = (14, 3, 21)

        points = [(24, 2, 28), (26, -20, -1), (-14, -23, -8), (11, 3, -7), (1, -11, -27), (29, 21, 21), (16, 14, 23), (-1, -17, 28), (20, -11, 3), (-24, 12, -24), (-2, 26, 11), (-3, 12, 26), (-14, -28, 2), (-26, -21, -15), (26, -23, 17), (-4, 12, 1), (27, -12, -19), (13, 0, 17), (21, 18, -25), (-1, 24, 22), (-30, 16, -10), (29, -25, 12), (24, 8, -15), (-19, -24, 17), (-6, -3, -23), (22, -6, 2), (-4, -17, -25), (-23, -22, 28), (22, 6, -27), (-22, -25, 11), (-8, -30, 0), (-19, -11, -27), (-14, -9, -11), (-21, -7, 0), (-28, -13, -14), (22, 4, 29), (12, -11, -20), (14, 12, -29), (17, -9, -28), (12, 28, -15), (22, -30, -26), (28, -22, 12), (17, 10, -9), (-3, 21, 17), (-20, -28, 2), (28, -7, 2), (17, 7, 9), (-30, -5, -8), (-13, 22, -5), (-14, -1, -8), (-27, 19, 22), (-4, 9, 23), (29, -21, -7), (25, 28, -9), (11, 17, -6), (18, -11, 28), (-7, 5, -23), (-2, -22, -29), (24, -19, 0), (-20, 6, 26), (16, 10, -26), (8, -14, 12), (2, 26, -26), (-9, -24, -4), (-16, -29, 5), (3, -8, -6), (-13, 17, 22), (-9, -28, -26), (15, -7, 13), (-3, -11, -9), (-1, 24, -22), (24, 11, -2), (-15, -29, -21), (-4, -19, -26), (-6, 16, -29), (-26, -2, -15), (13, 28, 0), (27, 22, -20), (24, -19, 1), (-21, -23, -4), (23, -23, -22), (0, -17, -8), (-17, 14, -28), (11, -29, -29), (2, -27, 27), (-3, 14, 11), (25, -7, -19), (18, -28, -29), (-23, 5, -21), (10, -11, -17), (-5, -17, 26), (-14, 29, 25), (12, -22, 15), (16, -20, -24), (-22, 26, -24), (22, -29, 19), (-26, -24, 11), (-7, 28, -3), (11, -30, 23), (20, -22, -20), (21, 10, -3), (18, -2, 26), (9, -20, 11), (-21, -28, 8), (6, 15, -1), (10, -21, -21), (-25, 11, -27), (14, -28, 2), (-29, 8, 17), (-1, 3, 13), (3, -20, 19), (14, -7, 13), (-11, 11, -16), (-26, 19, -22), (11, -29, 22), (11, -30, 27), (-27, 6, 18), (22, -17, 15), (-10, -15, -29), (25, 3, 18), (-8, 2, -11), (-10, 8, 25), (-30, 19, -7), (-5, 14, -15), (13, 6, 7), (-24, -3, -8), (22, 15, 20), (16, 22, -23), (-13, -4, -8), (-22, 25, -3), (19, 2, 27), (-15, -2, -5), (-26, -1, 10), (-4, -10, 23), (26, 24, -6), (-15, -15, 29), (-15, 18, -20), (-24, 9, 4), (-6, -18, 22), (13, -6, 19), (-3, -30, -2), (20, -8, -8), (22, -3, 6), (-21, 16, -29), (5, -10, 3), (-19, 25, 15), (17, -6, 24), (27, 16, 17), (-10, -7, -14), (-25, 24, 21), (5, -18, 23), (0, -19, -29), (23, -28, -12), (13, 13, -15), (3, 4, -25), (25, -12, 23), (-21, 10, 5), (24, -18, 9), (-18, 3, -22), (21, -12, -23), (-21, 27, -27), (21, -14, -11), (22, 18, 19), (5, 21, 7), (27, -4, -16), (-24, -21, -24), (18, 10, -18), (-27, -27, 27), (29, -29, 16), (16, 13, -12), (-26, 14, 0), (9, 10, 27), (-14, 9, 13), (13, -15, 29), (12, -27, -8), (7, 21, -18), (23, 16, -29), (-14, 21, -3), (-22, -28, -10), (-29, 14, -13), (-30, 28, 15), (29, -13, 24), (9, 26, 11), (-30, 2, 4), (4, 4, -19), (-30, 9, -28), (19, -21, -22), (-21, -7, -27), (1, 15, 13), (-10, 23, -29), (-9, -17, -3), (-20, 6, -29), (24, -20, -5), (26, 26, -15), (23, 5, 1), (-1, -30, 20), (1, 22, -5), (18, -6, -28), (-23, -2, -14), (-6, -9, 19)]

        known_range = []
        for (x, y, z) in points:
            if (x >= top_left[0]) and (x <= bottom_right[0]) and (y >= top_left[1]) and (y <= bottom_right[1]) and (z >= top_left[2]) and (z <= bottom_right[2]):
                known_range.append((x, y, z))
        known_range.sort()

        tree = kdtree.create(points)
        tree.rebalance()

        unknown_range = [x.data for x in tree.range_search(top_left, bottom_right)]
        unknown_range.sort()

        self.assertEqual(known_range, unknown_range)


def random_tree(nodes=20, dimensions=3, minval=0, maxval=100):
    points = list(islice(random_points(), 0, nodes))
    tree = kdtree.create(points)
    return tree

def random_point(dimensions=3, minval=0, maxval=100):
    return tuple(random.randint(minval, maxval) for _ in range(dimensions))

def random_points(dimensions=3, minval=0, maxval=100):
    while True:
        yield random_point(dimensions, minval, maxval)


if __name__ == "__main__":
    unittest.main()
