class PersistentSegmentTree:
    """Point-update persistent segment tree over a monoid.

    A root is an integer identifying one immutable version.  ``set`` returns a
    new root and never changes the version passed to it.  Ranges are half-open.

    ``values_or_n`` may be an iterable of initial values, or an integer size.
    In the latter case the initial version consists entirely of ``identity``
    and is represented without allocating all of its nodes.

    Example::

        seg = PersistentSegmentTree([1, 2, 3], lambda a, b: a + b, 0)
        root0 = seg.root
        root1 = seg.set(root0, 1, 10)
        assert seg.prod(root0, 0, 3) == 6
        assert seg.prod(root1, 0, 3) == 14

    Construction from values takes O(n) time and memory.  Each point update
    takes O(log n) time and additional memory, and each query takes O(log n)
    time.  ``op`` must be associative and ``identity`` must be its identity.
    """

    __slots__ = ("n", "op", "identity", "root", "_left", "_right", "_data")

    def __init__(self, values_or_n, op, identity):
        self.op = op
        self.identity = identity

        # Node 0 is an implicit subtree filled with the identity.  It makes an
        # identity-filled tree of any size cheap to construct.
        self._left = [0]
        self._right = [0]
        self._data = [identity]

        if isinstance(values_or_n, int):
            if values_or_n < 0:
                raise ValueError("size must be non-negative")
            self.n = values_or_n
            self.root = 0
        else:
            values = list(values_or_n)
            self.n = len(values)
            self.root = self._build(values, 0, self.n) if self.n else 0

    def _new_node(self, left, right, value):
        node = len(self._data)
        self._left.append(left)
        self._right.append(right)
        self._data.append(value)
        return node

    def _build(self, values, left, right):
        if right - left == 1:
            return self._new_node(0, 0, values[left])

        middle = (left + right) >> 1
        left_node = self._build(values, left, middle)
        right_node = self._build(values, middle, right)
        return self._new_node(
            left_node,
            right_node,
            self.op(self._data[left_node], self._data[right_node]),
        )

    def _check_root(self, root):
        if not isinstance(root, int) or not 0 <= root < len(self._data):
            raise IndexError("invalid root")

    def set(self, root, index, value):
        """Return a new root in which ``a[index]`` is replaced by ``value``."""
        self._check_root(root)
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        return self._set(root, 0, self.n, index, value)

    def _set(self, node, left, right, index, value):
        if right - left == 1:
            return self._new_node(0, 0, value)

        middle = (left + right) >> 1
        left_node = self._left[node]
        right_node = self._right[node]
        if index < middle:
            left_node = self._set(left_node, left, middle, index, value)
        else:
            right_node = self._set(right_node, middle, right, index, value)

        return self._new_node(
            left_node,
            right_node,
            self.op(self._data[left_node], self._data[right_node]),
        )

    def get(self, root, index):
        """Return ``a[index]`` in the version identified by ``root``."""
        self._check_root(root)
        if not 0 <= index < self.n:
            raise IndexError("index out of range")

        node = root
        left = 0
        right = self.n
        while node and right - left > 1:
            middle = (left + right) >> 1
            if index < middle:
                node = self._left[node]
                right = middle
            else:
                node = self._right[node]
                left = middle
        return self._data[node]

    def prod(self, root, query_left, query_right):
        """Fold ``a[query_left:query_right]`` in left-to-right order."""
        self._check_root(root)
        if not 0 <= query_left <= query_right <= self.n:
            raise IndexError("invalid range")
        return self._prod(root, 0, self.n, query_left, query_right)

    def _prod(self, node, left, right, query_left, query_right):
        if node == 0 or query_right <= left or right <= query_left:
            return self.identity
        if query_left <= left and right <= query_right:
            return self._data[node]

        middle = (left + right) >> 1
        return self.op(
            self._prod(self._left[node], left, middle, query_left, query_right),
            self._prod(self._right[node], middle, right, query_left, query_right),
        )

    def all_prod(self, root):
        """Return the fold of every value in the specified version."""
        self._check_root(root)
        return self._data[root]

    @property
    def node_count(self):
        """Number of allocated nodes, excluding the implicit identity node."""
        return len(self._data) - 1
