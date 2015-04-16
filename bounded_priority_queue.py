#!/usr/bin/env python
#
# Based on the work of Pravin Paratey (April 15, 2011)
# Joachim Hagege (June 18, 2014)
#
# Code released under BSD license
#
DISTANCE_INDEX = 1

class BoundedPriorityQueue:
    """ This class illustrates a PriorityQueue and its associated functions """

    def __init__(self, k):
        self.heap = []
        self.k = k

    def items(self):
        return self.heap

    def parent(self, index):
        """
        Parent will be at math.floor(index/2).
        """
        return int(index / 2)

    def left_child(self, index):
        return 2 * index + 1

    def right_child(self, index):
        return 2 * index + 2

    def max_heapify(self, index):
        """
        Responsible for maintaining the heap property of the heap.
        This function assumes that the subtree located at left and right
        child satisfies the max-heap property. But the tree at index
        (current node) does not. O(log n)
        """
        left_index = self.left_child(index)
        right_index = self.right_child(index)

        largest = index
        if left_index < len(self.heap) and self._dist(left_index) > self._dist(index):
            largest = left_index
        if right_index < len(self.heap) and self._dist(right_index) > self._dist(largest):
            largest = right_index

        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self.max_heapify(largest)

    def _dist(self, index):
        """ Get the distance of the heap object at the given index """
        return self.heap[index][DISTANCE_INDEX]

    def propagate_up(self, index):
        """ Compares index with parent and swaps node if larger O(log(n)) """
        while index != 0 and self._dist(self.parent(index)) < self._dist(index):
            self.heap[index], self.heap[self.parent(index)] = self.heap[self.parent(index)], self.heap[index]
            index = self.parent(index)

    def add(self, obj):
        """
        Add obj to the priority queue if it has a lower value than
        the maximum already in the queue. If the queue is full,
        then the object with the maximum value on the queue is
        replaced by this one.
        """
        size = self.size()

        # Size == k, The priority queue is at capacity.
        if size == self.k:
            max_elem = self.max()

            # The new element has a lower distance than the biggest one.
            # Then we insert, otherwise, don't insert.
            if obj[DISTANCE_INDEX] < max_elem:
                self.extract_max()
                self.heap_append(obj)

        # if size == 0 or 0 < Size < k
        else:
            self.heap_append(obj)

    def heap_append(self, obj):
        """ Adds an element in the heap O(ln(n)) """
        self.heap.append(obj)
        # Index value is 1 less than length:
        self.propagate_up(len(self.heap) - 1)

    def max(self):
        # The highest distance will always be at the index 0 (heap invariant)
        return self.heap[0][1]

    def size(self):
        return len(self.heap)

    def extract_max(self):
        """
        Part of the Priority Queue, extracts the element on the top of the heap
        and then re-heapifies. O(log n).
        """
        max = self.heap[0]
        data = self.heap.pop()
        if len(self.heap) > 0:
            self.heap[0] = data
            self.max_heapify(0)
        return max
