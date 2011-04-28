from __future__ import absolute_import

from random import random
from itertools import islice

import kdtree


def random_tree(nodes=20, dimensions=3, scale=100):
    points = list(islice(random_points(), 0, nodes))
    tree = kdtree.create(points)
    return tree

def random_point(dimensions, scale):
    return tuple(int(random() * scale) for _ in range(dimensions))

def random_points(dimensions=3, scale=100):
    while True:
        yield random_point(dimensions, scale)
