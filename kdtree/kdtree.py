import math
from itertools import chain
from collections import deque


class Node(object):
    """ A Node in a kd-tree

    A tree is represented by its root node, and every node represents
    its subtree"""

    def __init__(self, data=None, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right


    @property
    def is_leaf(self):
        """ Returns True if a Node has no subnodes

        >>> Node().is_leaf
        True

        >>> Node( 1, left=Node(2) ).is_leaf
        False
        """
        return (not self.data) or \
               (all(not bool(c) for c, p in self.children))


    def preorder(self):
        if not self:
            return

        yield self

        if self.left:
            for x in self.left.preorder():
                yield x

        if self.right:
            for x in self.right.preorder():
                yield x


    def inorder(self):
        if not self:
            return

        if self.left:
            for x in self.left.inorder():
                yield x

        yield self

        if self.right:
            for x in self.right.inorder():
                yield x


    def postorder(self):
        if not self:
            return

        if self.left:
            for x in self.left.postorder():
                yield x

        if self.right:
            for x in self.right.postorder():
                yield x

        yield self


    @property
    def children(self):
        """
        Returns an iterator for the non-empty children of the Node

        >>> len(list(create(dimensions=2).children))
        0

        >>> len(list(create([ (1, 2) ]).children))
        0

        >>> len(list(create([ (2, 2), (2, 1), (2, 3) ]).children))
        2
        """

        if self.left and self.left.data is not None:
            yield self.left, 0
        if self.right and self.right.data is not None:
            yield self.right, 1


    def set_child(self, index, child):
        if index == 0:
            self.left = child
        else:
            self.right = child


    def height(self):
        """
        Returns height of the (sub)tree, without considering
        empty leaf-nodes

        >>> create(dimensions=2).height()
        0

        >>> create([ (1, 2) ]).height()
        1

        >>> create([ (1, 2), (2, 3) ]).height()
        2
        """

        min_height = int(bool(self))
        return max([min_height] + [c.height()+1 for c, p in self.children])


    def get_child_pos(self, child):
        for c, pos in self.children:
            if child == c:
                return pos


    def __repr__(self):
        return '<%(cls)s - %(data)s>' % \
            dict(cls=self.__class__.__name__, data=repr(self.data))


    def __nonzero__(self):
        return self.data is not None

    def __eq__(self, other):
        if isinstance(other, tuple):
            return self.data == other
        else:
            return self.data == other.data



def require_axis(f):
    """ Check if the object of the function has axis and sel_axis members """

    def _wrapper(self, *args, **kwargs):
        if None in (self.axis, self.sel_axis):
            raise ValueError('%(func_name) requires the node %(node)s '
                    'to have an axis and a sel_axis function' %
                    dict(func_name=f.func_name, node=repr(self)))

        return f(self, *args, **kwargs)

    return _wrapper



class KDNode(Node):


    def __init__(self, data=None, left=None, right=None, axis=None,
            sel_axis=None):
        """ Creates a new node for a kd-tree

        If the node will be used within a tree, the axis and the sel_axis
        function should be supplied.

        sel_axis(axis) is used when creating subnodes of the current node. It
        receives the axis of the parent node and returns the axis of the child
        node. """

        super(KDNode, self).__init__(data, left, right)
        self.axis = axis
        self.sel_axis = sel_axis


    @require_axis
    def add(self, point):
        """
        Adds a point to the current node or recursively
        descends to one of its children.

        Users should call add() only to the topmost tree.
        """

        if self.data is None:
            self.data = point
            return

        dim = check_dimensionality([self.data, point])

        if point[self.axis] < self.data[self.axis]:
            if self.left is None:
                self.left = self.create_subnode(point)
            else:
                self.left.add(point)

        else:
            if self.right is None:
                self.right = self.create_subnode(point)
            else:
                self.right.add(point)


    @require_axis
    def create_subnode(self, data):
        return self.__class__(data,
                axis=self.sel_axis(self.axis),
                sel_axis=self.sel_axis)


    @require_axis
    def find_replacement(self):
        if self.right:
            child, parent = self.right.extreme_child(min, self.axis)
        else:
            child, parent = self.left.extreme_child(max, self.axis)

        return (child, parent if parent is not None else self)



    @require_axis
    def remove(self, point):
        """ Removes the node with the given point from the tree

        Returns the new root node of the (sub)tree """

        if not self:
            return

        if self.data == point:

            if self.is_leaf:
                self.data = None
                return self

            else:
                root, max_p = self.find_replacement()

                pos = max_p.get_child_pos(root)

                # self and root swap positions
                tmp_l, tmp_r = self.left, self.right
                self.left, self.right = root.left, root.right
                root.left, root.right = tmp_l if tmp_l is not root else self, tmp_r if tmp_r is not root else self
                self.axis, root.axis = root.axis, self.axis


                if max_p is not self:
                    max_p.set_child(pos, self)
                    new_depth = max_p.height()
                    max_p.remove(self.data)

                else:
                    root.remove(self.data)

                return root


        if self.left and self.left.data == point:
            if self.left.is_leaf:
                self.left = None

            else:
                self.left = self.left.remove(point)


        elif self.right and self.right.data == point:
            if self.right.is_leaf:
                self.right = None

            else:
                self.right = self.right.remove(point)


        if point[self.axis] <= self.data[self.axis]:
            if self.left:
                self.left = self.left.remove(point)

        if point[self.axis] >= self.data[self.axis]:
            if self.right:
                self.right = self.right.remove(point)

        return self


    @property
    def is_balanced(self):
        left_height = self.left.height() if self.left else 0
        right_height = self.right.height() if self.right else 0

        if abs(left_height - right_height) > 1:
            return False

        return all(c.is_balanced for c, _ in self.children)


    def rebalance(self):
        """
        Returns the (possibly new) root of the rebalanced tree
        """
        return create(list([x.data for x in self.inorder()]))


    def axis_dist(self, point, axis):
        """
        Squared distance at the given axis between
        the current Node and the given point
        """
        import math
        return math.pow(self.data[axis] - point[axis], 2)


    def dist(self, point):
        """
        Squared distance between the current Node
        and the given point
        """
        r = range(len(self.data))
        return sum([self.axis_dist(point, i) for i in r])


    @require_axis
    def search_nn(self, point, best=None):
        """
        Search the nearest neighbor of the given point
        """

        if best is None:
            best = self

        # consider the current node
        if self.dist(point) < best.dist(point):
            best = self

        # sort the children, nearer one first
        children = sorted(self.children, key=lambda (c, p): c.dist(point))

        for child, p in children:
            # check if node needs to be recursed
            if self.axis_dist(point, self.axis) < best.dist(point):
                best = child.search_nn(point, best)

        return best


    @require_axis
    def is_valid(self):
        if not self:
            return True

        if self.left and self.data[self.axis] < self.left.data[self.axis]:
            return False

        if self.right and self.data[self.axis] > self.right.data[self.axis]:
            return False

        return all(c.is_valid() for c, _ in self.children) or self.is_leaf


    def extreme_child(self, sel_func, axis):
        """ Returns a child of the subtree and its parent

        The child is selected by sel_func which is either min or max
        (or a different function with similar semantics). """

        max_key = lambda (child, parent): child.data[axis]


        # we don't know our parent, so we include None
        me = [(self, None)] if self else []

        child_max = [c.extreme_child(sel_func, axis) for c, _ in self.children]
        # insert self for unknown parents
        child_max = [(c, p if p is not None else self) for c, p in child_max]

        candidates =  me + child_max

        if not candidates:
            return None, None

        return sel_func(candidates, key=max_key)



def create(point_list=[], dimensions=None, axis=0, sel_axis=None):
    """ Creates a kd-tree from a list of points

    All points in the list must be of the same dimensionality.

    If no point_list is given, an empty tree is created. The number of
    dimensions has to be given instead.

    If both a point_list and dimensions are given, the numbers must agree.

    Axis is the axis on which the root-node should split.

    sel_axis(axis) is used when creating subnodes of a node. It receives the
    axis of the parent node and returns the axis of the child node. """

    if not point_list and not dimensions:
        raise ValueError('either point_list or dimensions must be provided')

    elif point_list:
        dim = check_dimensionality(point_list)
        dimensions = dim
    else:
        dim = dimensions


    if dim != dimensions:
        raise ValueError('dimensions parameter must match actual dimension of points')

    # by default cycle through the axis
    sel_axis = sel_axis or (lambda prev_axis: (prev_axis+1) % dim)

    if not point_list:
        return KDNode(sel_axis=sel_axis, axis=axis)

    # Sort point list and choose median as pivot element
    point_list.sort(key=lambda point: point[axis])
    median = len(point_list) // 2

    loc   = point_list[median]
    left  = create(point_list[:median], dim, sel_axis(axis))
    right = create(point_list[median + 1:], dim, sel_axis(axis))
    return KDNode(loc, left, right, axis=axis, sel_axis=sel_axis)


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

        if include_all or node.left:
            q.append(node.left or node.__class__())

        if include_all or node.right:
            q.append(node.right or node.__class__())



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

        width = int(max_width*node_width/per_level)

        node_str = (str(node.data) if node else '').center(width)
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
