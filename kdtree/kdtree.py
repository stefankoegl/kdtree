class Node(object):

    def __init__(self, location, left_child, right_child):
        self.location = location
        self.left_child = left_child
        self.right_child = right_child

    def __repr__(self):
        return '<Node at %s>' % repr(self.location)


def kdtree(point_list, depth=0):
    if not point_list:
        return

    # Select axis by cycling through them
    dim = check_dimensionality(point_list)
    axis = depth % dim

    # Sort point list and choose median as pivot element
    point_list.sort(key=lambda point: point[axis])
    median = len(point_list) // 2

    loc   = point_list[median]
    left  = kdtree(point_list[:median], depth + 1)
    right = kdtree(point_list[median + 1:], depth + 1)
    return Node(loc, left, right)


def check_dimensionality(point_list):
    dimension = len(point_list[0])
    for p in point_list[1:]:
        if len(p) != dimension:
            raise ValueError('All Points in the point_list must have the same dimensionality')

    return dimension
