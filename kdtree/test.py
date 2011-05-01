from __future__ import absolute_import

import random
from itertools import islice

import kdtree


def random_tree(nodes=20, dimensions=3, minval=0, maxval=100):
    points = list(islice(random_points(), 0, nodes))
    tree = kdtree.create(points)
    return tree

def random_point(dimensions, minval, maxval):
    return tuple(random.randint(minval, maxval) for _ in range(dimensions))

def random_points(dimensions=3, minval=0, maxval=100):
    while True:
        yield random_point(dimensions, minval, maxval)
