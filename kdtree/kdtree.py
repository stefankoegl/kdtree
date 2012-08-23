import math
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
        """ iterator for nodes: root, left, right """

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
        """ iterator for nodes: left, root, right """

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
        """ iterator for nodes: left, right, root """

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

        The children are returned as (Node, pos) tuples where pos is 0 for the
        left subnode and 1 for the right.

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
        """ Sets one of the node's children

        index 0 refers to the left, 1 to the right child """

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
        """ Returns the position if the given child

        If the given node is the left child, 0 is returned. If its the right
        child, 1 is returned. Otherwise None """

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
    """ A Node that contains kd-tree specific data and methods """


    def __init__(self, data=None, left=None, right=None, axis=None,
            sel_axis=None, dimensions=None):
        """ Creates a new node for a kd-tree

        If the node will be used within a tree, the axis and the sel_axis
        function should be supplied.

        sel_axis(axis) is used when creating subnodes of the current node. It
        receives the axis of the parent node and returns the axis of the child
        node. """

        super(KDNode, self).__init__(data, left, right)
        self.axis = axis
        self.sel_axis = sel_axis
        self.dimensions = dimensions


    @require_axis
    def add(self, point):
        """
        Adds a point to the current node or recursively
        descends to one of its children.

        Users should call add() only to the topmost tree.
        """

        check_dimensionality([point], dimensions=self.dimensions)

        # Adding has hit an empty leaf-node, add here
        if self.data is None:
            self.data = point
            return

        # split on self.axis, recurse either left or right
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
        """ Creates a subnode for the current node """

        return self.__class__(data,
                axis=self.sel_axis(self.axis),
                sel_axis=self.sel_axis,
                dimensions=self.dimensions)


    @require_axis
    def find_replacement(self):
        """ Finds a replacement for the current node

        The replacement is returned as a
        (replacement-node, replacements-parent-node) tuple """

        if self.right:
            child, parent = self.right.extreme_child(min, self.axis)
        else:
            child, parent = self.left.extreme_child(max, self.axis)

        return (child, parent if parent is not None else self)



    @require_axis
    def remove(self, point):
        """ Removes the node with the given point from the tree

        Returns the new root node of the (sub)tree """

        # Recursion has reached an empty leaf node, nothing here to delete
        if not self:
            return


        # Recursion has reached the node to be deleted
        if self.data == point:

            if self.is_leaf:
                self.data = None
                return self

            else:
                # find a replacement for the node (will be the new subtree-root)
                root, max_p = self.find_replacement()

                pos = max_p.get_child_pos(root)

                # self and root swap positions
                tmp_l, tmp_r = self.left, self.right
                self.left, self.right = root.left, root.right
                root.left, root.right = tmp_l if tmp_l is not root else self, tmp_r if tmp_r is not root else self
                self.axis, root.axis = root.axis, self.axis


                # Special-case if we have chosen a direct child as the replacement
                if max_p is not self:
                    max_p.set_child(pos, self)
                    new_depth = max_p.height()
                    max_p.remove(self.data)

                else:
                    root.remove(self.data)

                return root


        # Remove direct subnode
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


        # Recurse to subtrees
        if point[self.axis] <= self.data[self.axis]:
            if self.left:
                self.left = self.left.remove(point)

        if point[self.axis] >= self.data[self.axis]:
            if self.right:
                self.right = self.right.remove(point)

        return self


    @property
    def is_balanced(self):
        """ Returns True if the (sub)tree is balanced

        The tree is balanced if the heights of both subtrees differ at most by
        1 """

        left_height = self.left.height() if self.left else 0
        right_height = self.right.height() if self.right else 0

        if abs(left_height - right_height) > 1:
            return False

        return all(c.is_balanced for c, _ in self.children)


    def rebalance(self):
        """
        Returns the (possibly new) root of the rebalanced tree
        """

        return create([x.data for x in self.inorder()])


    def axis_dist(self, point, axis):
        """
        Squared distance at the given axis between
        the current Node and the given point
        """
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
        Search the nearest node of the given point

        point must be a location, not a node. The nearest node to the point is
        returned. If a location of an actual node is used, the Node with this
        location will be retuend (not its neighbor) """

        if best is None:
            best = self

        # consider the current node
        if self.dist(point) < best.dist(point):
            best = self

        # sort the children, nearer one first
        children = iter(sorted(self.children, key=lambda (c, p): c.axis_dist(point, self.axis)))


        c1, _ = next(children, (None, None))
        if c1:
            best = c1.search_nn(point, best)

        c2, _ = next(children, (None, None))
        if c2 and self.axis_dist(point, self.axis) < best.dist(point):
            best = c2.search_nn(point, best)

        return best


    @require_axis
    def search_nn_dist(self, point, distance, best=[]):
        """
        Search the n nearest nodes of the given point which are within given
        distance

        point must be a location, not a node. A list containing the n nearest
        nodes to the point within the distance will be returned.
        """

        # consider the current node
        if self.dist(point) < distance:
            best.append(self)

        # sort the children, nearer one first (is this really necessairy?)
        children = sorted(self.children, key=lambda (c, p): c.dist(point))

        for child, p in children:
            # check if child node needs to be recursed
            if self.axis_dist(point, self.axis) < distance:
                child.search_nn_dist(point, distance, best)

        return best


    @require_axis
    def is_valid(self):
        """ Checks recursively if the tree is valid

        It is valid if each node splits correctly """

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
        dimensions = check_dimensionality(point_list, dimensions)

    # by default cycle through the axis
    sel_axis = sel_axis or (lambda prev_axis: (prev_axis+1) % dimensions)

    if not point_list:
        return KDNode(sel_axis=sel_axis, axis=axis, dimensions=dimensions)

    # Sort point list and choose median as pivot element
    point_list.sort(key=lambda point: point[axis])
    median = len(point_list) // 2

    loc   = point_list[median]
    left  = create(point_list[:median], dimensions, sel_axis(axis))
    right = create(point_list[median + 1:], dimensions, sel_axis(axis))
    return KDNode(loc, left, right, axis=axis, sel_axis=sel_axis)


def check_dimensionality(point_list, dimensions=None):
    dimensions = dimensions or len(point_list[0])
    for p in point_list:
        if len(p) != dimensions:
            raise ValueError('All Points in the point_list must have the same dimensionality')

    return dimensions



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
