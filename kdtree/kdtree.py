import math
from itertools import chain
from collections import deque


class Node(object):
    """ A Node in a kd-tree

    A tree is represented by its root node, and every node represents
    its subtree"""

    def __init__(self, location=None, left_child=None, right_child=None):
        self.location = location
        self.left_child = left_child
        self.right_child = right_child


    def add(self, point, depth=0):
        """
        Adds a point to the current node or recursively
        descends to one of its children.

        Users should call add() only to the topmost tree node or
        pass the correct depth if they call for deeper nodes.
        """

        if self.location is None:
            self.location = point
            return

        dim = check_dimensionality([self.location, point])
        axis = select_axis(dim, depth)

        if point[axis] < self.location[axis]:
            if self.left_child is None:
                self.left_child = Node(point)
            else:
                self.left_child.add(point, depth+1)

        else:
            if self.right_child is None:
                self.right_child = Node(point)
            else:
                self.right_child.add(point, depth+1)


    def remove(self, point, depth=0):
        """ Removes the node with the given point from the tree

        Returns the new root node of the (sub)tree """

        dim = check_dimensionality([self.location])
        axis = select_axis(dim, depth)


        if self.location == point:
            max_c, max_p, pos = self.max_child()
            root = max_c

            for child, p in self.children:
                if child is not root:
                    root.set_child(p, child)

            self.left_child = None
            self.right_child = None

            root.remove(self.location)
            return root


        if self.left_child and self.left_child.location == point:
            if self.left_child.is_leaf:
                self.left_child = None

            elif len(list(self.left_child.children)) == 1:
                self.left_child = self.left_child.left_child or \
                                  self.left_child.right_child

            else:
                self.left_child = self.left_child.remove(point, depth+1)


        elif self.right_child and self.right_child.location == point:
            if self.right_child.is_leaf:
                self.right_child = None

            elif len(list(self.right_child.children)) == 1:
                self.right_child = self.right_child.left_child or \
                                   self.right_child.right_child

            else:
                self.right_child = self.right_child.remove(point, depth+1)


        elif point[axis] < self.location[axis]:
            if self.left_child:
                self.left_child.remove(point, depth+1)

        elif point[axis] > self.location[axis]:
            if self.right_child:
                self.right_child.remove(point, depth+1)

        return self


    def max_child(self):
        """ Returns the maximum child of the subtree and its parent """

        if self.right_child and list(self.right_child.children):
            return self.right_child.max_child()
        return (self.right_child, self, 1)

    def min_child(self):
        """ Returns the minimum child of the subtree and its parent """

        if self.left_child and list(self.left_child.children):
            return self.left_child.min_child()
        return (self.left_child, self, 0)


    @property
    def is_leaf(self):
        return (not self.location) or \
               (all(not bool(c) for c, p in self.children))


    def preorder(self):
        yield self

        if self.left_child:
            for x in self.left_child.preorder():
                yield x

        if self.right_child:
            for x in self.right_child.preorder():
                yield x


    def inorder(self):
        if self.left_child:
            for x in self.left_child.inorder():
                yield x

        yield self

        if self.right_child:
            for x in self.right_child.inorder():
                yield x


    def postorder(self):
        if self.left_child:
            for x in self.left_child.postorder():
                yield x

        if self.right_child:
            for x in self.right_child.postorder():
                yield x

        yield self


    def rebalance(self):
        """
        Returns the (possibly new) root of the rebalanced tree
        """
        return create(self.inorder())


    def axis_dist(self, point, axis):
        """
        Squared distance at the given axis between
        the current Node and the given point
        """
        import math
        return math.pow(self.location[axis] - point[axis], 2)


    def dist(self, point):
        """
        Squared distance between the current Node
        and the given point
        """
        r = range(len(self.location))
        return sum([self.axis_dist(point, i) for i in r])


    def search_nn(self, point, best=None, depth=0):
        """
        Search the nearest neighbor of the given point
        """

        if best is None:
            best = self

        # consider the current node
        if self.dist(point) < best.dist(point):
            best = self

        # sort the children, nearer one first
        children = sorted(self.children, key=lambda c, p: c.dist(point))

        axis = select_axis(len(self.location), depth)

        for child, p in children:
            # check if node needs to be recursed
            if self.axis_dist(point, axis) < best.dist(point):
                best = child.search_nn(point, best, depth+1)

        return best


    @property
    def children(self):
        """
        Returns an iterator for the non-empty children of the Node

        >>> len(list(create().children()))
        0

        >>> len(list(create([ (1, 2) ]).children()))
        0

        >>> len(list(create([ (2, 2), (2, 1), (2, 3) ]).children()))
        2
        """

        if self.left_child and self.left_child.location is not None:
            yield self.left_child, 0
        if self.right_child and self.right_child.location is not None:
            yield self.right_child, 1


    def set_child(self, index, child):
        if index == 0:
            self.left_child = child
        else:
            self.right_hild = child


    def height(self):
        """
        Returns height of the (sub)tree, without considering
        empty leaf-nodes

        >>> create().height()
        0

        >>> create([ (1, 2) ]).height()
        1

        >>> create([ (1, 2), (2, 3) ]).height()
        2
        """

        min_height = int(bool(self))
        return max([min_height] + [c.height()+1 for c, p in self.children])


    def __repr__(self):
        return '<Node at %s>' % repr(self.location)


    def __nonzero__(self):
        return self.location is not None

    def __eq__(self, other):
        if isinstance(other, tuple):
            return self.location == other
        else:
            return super(Node, self).__eq__(other)


def select_axis(dimensions, depth):
    """
    Select axis by cycling through them
    """
    return depth % dimensions


def create(point_list=[], depth=0):
    """ Creates a kd-tree from a list of points """

    if not point_list:
        return Node()

    dim = check_dimensionality(point_list)
    axis = select_axis(dim, depth)

    # Sort point list and choose median as pivot element
    point_list.sort(key=lambda point: point[axis])
    median = len(point_list) // 2

    loc   = point_list[median]
    left  = create(point_list[:median], depth + 1)
    right = create(point_list[median + 1:], depth + 1)
    return Node(loc, left, right)


def check_dimensionality(point_list):
    dimension = len(point_list[0])
    for p in point_list[1:]:
        if len(p) != dimension:
            raise ValueError('All Points in the point_list must have the same dimensionality')

    return dimension



def level_order(tree, include_all=False):
    """ Returns an iterator over the tree in level-order

    If include_all is set to True, empty parts of the tree are filled
    with dummy entries and the iterator becomes infinite. """

    q = deque()
    q.append(tree)
    while q:
        node = q.popleft()
        yield node

        if include_all or node.left_child:
            q.append(node.left_child or Node())

        if include_all or node.right_child:
            q.append(node.right_child or Node())



def visualize(tree, max_level=100, node_width=10, left_padding=5):
    """ Prints the tree to stdout """

    height = min(max_level, tree.height()-1)
    max_width = pow(2, height)

    per_level = 1
    in_level  = 0
    level     = 0

    for node in level_order(tree, include_all=True):

        if in_level == 0:
            print
            print
            print ' '*left_padding,

        width = max_width*node_width/per_level

        node_str = (str(node.location) if node else '').center(width)
        print node_str,

        in_level += 1

        if in_level == per_level:
            in_level   = 0
            per_level *= 2
            level     += 1

        if level > height:
            break

    print
    print
