A simple kd-tree in Python [![Build Status](https://travis-ci.org/stefankoegl/kdtree.png?branch=master)](https://travis-ci.org/stefankoegl/kdtree)
==========================

The kdtree package can construct, modify and search
[kd-trees](http://en.wikipedia.org/wiki/Kd-tree).

* Website: https://github.com/stefankoegl/kdtree
* Repository: https://github.com/stefankoegl/kdtree.git
* Documentation: https://python-kdtree.readthedocs.org/
* PyPI: https://pypi.python.org/pypi/kdtree
* Travis-CI: https://travis-ci.org/stefankoegl/kdtree
* Coveralls: https://coveralls.io/r/stefankoegl/kdtree


Usage
-----

    >>> import kdtree

    # Create an empty tree by specifying the number of
    # dimensions its points will have
    >>> emptyTree = kdtree.create(dimensions=3)

    # A kd-tree can contain different kinds of points, for example tuples
    >>> point1 = (2, 3, 4)

    # Lists can also be used as points
    >>> point2 = [4, 5, 6]

    # Other objects that support indexing can be used, too
    >>> import collections
    >>> Point = collections.namedtuple('Point', 'x y z')
    >>> point3 = Point(5, 3, 2)

    # A tree is created from a list of points
    >>> tree = kdtree.create([point1, point2, point3])

    # Each (sub)tree is represented by its root node
    >>> tree
    <KDNode - [4, 5, 6]>

    # Adds a tuple to the tree
    >>> tree.add( (5, 4, 3) )

    # Removes the previously added point and returns the new root
    >>> tree = tree.remove( (5, 4, 3) )

    # Retrieving the Tree in inorder
    >>> list(tree.inorder())
    [<KDNode - (2, 3, 4)>, <KDNode - [4, 5, 6]>, <KDNode - Point(x=5, y=3, z=2)>]

    # Retrieving the Tree in level order
    >>> list(kdtree.level_order(tree))
    [<KDNode - [4, 5, 6]>, <KDNode - (2, 3, 4)>, <KDNode - Point(x=5, y=3, z=2)>]

    # Find the nearest node to the location (1, 2, 3)
    >>> tree.search_nn( (1, 2, 3) )
    <KDNode - (2, 3, 4)>

    # Add a point to make the tree more interesting
    >>> tree.add( (10, 2, 1) )

    # Visualize the Tree
    >>> kdtree.visualize(tree)


                         [4, 5, 6]

               (2, 3, 4)       Point(x=5, y=3, z=2)

                                (10, 2, 1)

    # Take the right subtree of the root
    >>> subtree = tree.right

    # and detatch it
    >>> tree.right = None
    >>> kdtree.visualize(tree)

               [4, 5, 6]

          (2, 3, 4)

    >>> kdtree.visualize(subtree)

          Point(x=5, y=3, z=2)

          (10, 2, 1)

    # and re-attach it
    >>> tree.right = subtree
    >>> kdtree.visualize(tree)

                         [4, 5, 6]

               (2, 3, 4)       Point(x=5, y=3, z=2)

                                (10, 2, 1)

    # Add a node to make the tree unbalanced
    >>> tree.is_balanced
    True
    >>> tree.add( (6, 1, 5) )
    >>> tree.is_balanced
    False
    >>> kdtree.visualize(tree)

                                       [4, 5, 6]

                   (2, 3, 4)                           Point(x=5, y=3, z=2)
                                                   (10, 2, 1)
                                                           (6, 1, 5)
    # rebalance the tree
    >>> tree = tree.rebalance()
    >>> tree.is_balanced
    True
    >>> kdtree.visualize(tree)

                    Point(x=5, y=3, z=2)

               [4, 5, 6]            (6, 1, 5)

          (2, 3, 4)

### Adding a payload

Indexing a dict by a pair of floats is not a good idea, since there might be unexpected precision errors.
Since KDTree expects a tuple-looking objects for nodes, you can make a class that looks like a tuple, but
contains more data. This way you can store all your data in a kdtree, without using an additional
indexed structure.

```python
import kdtree

# This class emulates a tuple, but contains a useful payload
class Item(object):
    def __init__(self, x, y, data):
        self.coords = (x, y)
        self.data = data

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, i):
        return self.coords[i]

    def __repr__(self):
        return 'Item({}, {}, {})'.format(self.coords[0], self.coords[1], self.data)

# Now we can add Items to the tree, which look like tuples to it
point1 = Item(2, 3, 'First')
point2 = Item(3, 4, 'Second')
point3 = Item(5, 2, ['some', 'list'])

# Again, from a list of points
tree = kdtree.create([point1, point2, point3])

#  The root node
print(tree)

# ...contains "data" field with an Item, which contains the payload in "data" field
print(tree.data.data)

# All functions work as intended, a payload is never lost
print(tree.search_nn([1, 2]))
```

Prints:

```
<KDNode - Item(3, 4, Second)>
Second
(<KDNode - Item(2, 3, First)>, 2.0)
```
