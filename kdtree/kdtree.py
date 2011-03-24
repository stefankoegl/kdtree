class Node(object):

    def __init__(self, location, left_child, right_child):
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
                self.left_child = Node(point, None, None)
            else:
                self.left_child.add(point, depth+1)

        else:
            if self.right_child is None:
                self.right_child = Node(point, None, None)
            else:
                self.right_child.add(point, depth+1)


    def preorder(self):
        return ([self.location]              if self.location    else [])+ \
               (self.left_child.preorder()   if self.left_child  else []) + \
               (self.right_child.preorder()  if self.right_child else [])

    def inorder(self):
        return (self.left_child.inorder()    if self.left_child  else []) + \
               ([self.location]              if self.location    else [])+ \
               (self.right_child.inorder()   if self.right_child else [])

    def postorder(self):
        return (self.left_child.postorder()  if self.left_child  else []) + \
               (self.right_child.postorder() if self.right_child else []) + \
               ([self.location]              if self.location    else [])


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
        children = sorted(self.children(), key=lambda p: p.dist(point))

        axis = select_axis(len(self.location), depth)

        for child in children:
            # check if node needs to be recursed
            if self.axis_dist(point, axis) < best.dist(point):
                best = child.search_nn(point, best, depth+1)

        return best


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
            yield self.left_child
        if self.right_child and self.right_child.location is not None:
            yield self.right_child


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

        min_height = int(bool(self.location))
        return max([min_height] + [c.height()+1 for c in self.children()])


    def __repr__(self):
        return '<Node at %s>' % repr(self.location)



def select_axis(dimensions, depth):
    """
    Select axis by cycling through them
    """
    return depth % dimensions


def create(point_list=[], depth=0):
    if not point_list:
        return Node(None, None, None)

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
