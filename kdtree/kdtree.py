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
    right = cretae(point_list[median + 1:], depth + 1)
    return Node(loc, left, right)


def check_dimensionality(point_list):
    dimension = len(point_list[0])
    for p in point_list[1:]:
        if len(p) != dimension:
            raise ValueError('All Points in the point_list must have the same dimensionality')

    return dimension
