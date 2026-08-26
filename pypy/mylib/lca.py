class LCA:
    """Lowest Common Ancestor by binary lifting.

    Construction: O(n log n)
    lca / distance / kth_ancestor / jump: O(log n)

    ``graph`` must be an adjacency list of a tree. Vertices are 0-indexed.
    """

    def __init__(self, graph, root=0):
        n = len(graph)
        if not 0 <= root < n:
            raise ValueError("root is out of range")

        self.n = n
        self.root = root
        self.depth = [-1] * n
        parent = [-1] * n
        self.depth[root] = 0

        stack = [root]
        while stack:
            v = stack.pop()
            for to in graph[v]:
                if to == parent[v]:
                    continue
                if self.depth[to] != -1:
                    raise ValueError("graph must be a tree")
                parent[to] = v
                self.depth[to] = self.depth[v] + 1
                stack.append(to)

        if any(d == -1 for d in self.depth):
            raise ValueError("graph must be connected")

        self.log = 1
        while (1 << self.log) <= n:
            self.log += 1
        self.parent = [parent]
        for _ in range(1, self.log):
            prev = self.parent[-1]
            self.parent.append([prev[prev[v]] if prev[v] != -1 else -1 for v in range(n)])

    def kth_ancestor(self, v, k):
        """Return the k-th ancestor of v, or -1 if it does not exist."""
        if not 0 <= v < self.n:
            raise ValueError("vertex is out of range")
        if k < 0:
            raise ValueError("k must be non-negative")
        if k > self.depth[v]:
            return -1

        bit = 0
        while k:
            if k & 1:
                v = self.parent[bit][v]
            k >>= 1
            bit += 1
        return v

    def lca(self, u, v):
        """Return the lowest common ancestor of u and v."""
        if not (0 <= u < self.n and 0 <= v < self.n):
            raise ValueError("vertex is out of range")

        if self.depth[u] < self.depth[v]:
            u, v = v, u
        u = self.kth_ancestor(u, self.depth[u] - self.depth[v])
        if u == v:
            return u

        for bit in range(self.log - 1, -1, -1):
            if self.parent[bit][u] != self.parent[bit][v]:
                u = self.parent[bit][u]
                v = self.parent[bit][v]
        return self.parent[0][u]

    def distance(self, u, v):
        """Return the number of edges on the path from u to v."""
        w = self.lca(u, v)
        return self.depth[u] + self.depth[v] - 2 * self.depth[w]

    def jump(self, u, v, k):
        """Return the vertex k edges from u on the u-v path, or -1."""
        if k < 0:
            raise ValueError("k must be non-negative")
        w = self.lca(u, v)
        up = self.depth[u] - self.depth[w]
        down = self.depth[v] - self.depth[w]
        if k > up + down:
            return -1
        if k <= up:
            return self.kth_ancestor(u, k)
        return self.kth_ancestor(v, up + down - k)
