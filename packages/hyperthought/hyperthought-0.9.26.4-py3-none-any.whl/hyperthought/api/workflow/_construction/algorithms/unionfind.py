"""
unionfind.py

Implementation of the Union-Find algorithm for identifying connected components
in a graph.
"""

from collections import defaultdict


class UnionFind:
    """
    Implementation of the Union-Find algorithm for identifying connected
    components in a graph.

    This is a translation of the WeightedQuickUnionFind Java class found in
    Algorithms, 4th edition, Robert Sedgewick and Kevin Wayne, page 228.
    The modification involves translation from an arbitrary identifier to a
    list index.  The identifier will be obtained via the get_id function
    (constructor parameter) applied to a data object passed to one of the
    public methods.

    This implementation will also not require the size of the graph to be known
    beforehand.

    This implementation will also include a method to get connected components.

    Parameters
    ----------
    get_id : function
        A function to be used on a data input to extract a unique identifier.
        It will be the client's responsibility to ensure that the identifiers
        are in fact unique.
    """

    def __init__(self, get_id=None):
        if get_id is None:
            get_id = lambda x: x

        if not callable(get_id):
            raise ValueError("get_id must be a callable")

        # TODO:  Validate that get_id takes one parameter and returns a
        #        hashable value.

        self._get_id = get_id
        self._id_to_index = {}  # Translate from id to list index. (See below.)
        self._parent = []       # Analogous to the id array in Sedgewick/Wayne.
        self._size = []         # Analogous to the sz array in Sedgewick/Wayne.
        self._count = 0         # Number of connected components.

    @property
    def count(self):
        """The number of connected components."""
        return self._count

    def connected(self, data1, data2):
        """
        Determine whether two data objects belong to the same connected
        component.
        """
        id1 = self._get_id(data1)
        id2 = self._get_id(data2)

        if id1 not in self._id_to_index:
            self._add_data(data1)

        if id2 not in self._id_to_index:
            self._add_data(data2)

        index1 = self._id_to_index[self._get_id(data1)]
        index2 = self._id_to_index[self._get_id(data2)]
        return self._find(index1) == self._find(index2)

    def _add_data(self, id_):
        """Add information on a previously unseen data object."""
        assert id_ not in self._id_to_index, f"{id_} has already been seen."
        index = len(self._id_to_index)
        self._id_to_index[id_] = index
        # By default, the parent of a new element is itself.
        self._parent.append(index)
        # Thus, a new component has been added.
        self._count += 1
        # The size of the new component is 1.
        self._size.append(1)

    def _find(self, index):
        """
        Find the root of the tree representing the connected component
        that includes the data object of interest.

        Parameters
        ----------
        index : int
            An index for a data object.  Indexes self._parent and self._size.

        Returns
        -------
        The index of the root object in self._parents.
        """
        while self._parent[index] != index:
            index = self._parent[index]

        return index

    def union(self, data1, data2):
        """
        Connect the components involving two data objects.

        Parameters
        ----------
        data1 : object
            A data object.
            Requirement:  The get_id function passed to the constructor must
            be able to extract a unique id from the data object.
        data2 : object
            Same as data1.

        Result
        ------
        The components involving the two data objects will be connected if
        they weren't already.
        """
        id1 = self._get_id(data1)
        id2 = self._get_id(data2)

        if id1 not in self._id_to_index:
            self._add_data(id1)

        if id2 not in self._id_to_index:
            self._add_data(id2)

        index1 = self._id_to_index[id1]
        index2 = self._id_to_index[id2]
        root1 = self._find(index1)
        root2 = self._find(index2)

        if root1 == root2:
            return

        # Make smaller root point to larger one.
        if self._size[root1] < self._size[root2]:
            self._parent[root1] = root2
            self._size[root2] += self._size[root1]
        else:
            self._parent[root2] = root1
            self._size[root1] += self._size[root2]

        self._count -= 1

    def get_components(self):
        """
        Get connected components.

        Returns
        -------
        A list of lists.  Contents of the inner lists will be ids of data
        objects.
        """
        components = defaultdict(list)

        for id_, index in self._id_to_index.items():
            root = self._find(index)
            components[root].append(id_)

        return list(components.values())


if __name__ == '__main__':
    # Test Union-Find implementation.  Use the example from page 217 of
    # Sedgewick/Wayne.
    uf = UnionFind()
    uf.union(4, 3)
    uf.union(3, 8)
    uf.union(6, 5)
    uf.union(9, 4)
    uf.union(2, 1)
    uf.union(8, 9)
    uf.union(5, 0)
    uf.union(7, 2)
    uf.union(6, 1)
    uf.union(1, 0)
    uf.union(6, 7)
    assert uf.count == 2
    assert uf.connected(3, 4)
    assert uf.connected(8, 9)
    assert uf.connected(3, 9)
    assert not uf.connected(1, 9)
    print("Components:", uf.get_components())
