import random
import sys
import unittest
from collections import deque
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mylib.rerooting import Rerooting


class RerootingTest(unittest.TestCase):
    def test_subtree_size_from_every_root(self):
        rr = Rerooting(
            5,
            identity=0,
            merge=lambda a, b: a + b,
            add_vertex=lambda x, _v: x + 1,
            add_edge=lambda x, _src, _dst, _data: x,
        )
        for u, v in [(0, 1), (1, 2), (1, 3), (3, 4)]:
            rr.add_edge(u, v, None)

        self.assertEqual(rr.solve(), [5] * 5)

    def test_weighted_distance_sums(self):
        rr = Rerooting(
            4,
            identity=(0, 0),
            merge=lambda a, b: (a[0] + b[0], a[1] + b[1]),
            add_vertex=lambda x, _v: (x[0] + 1, x[1]),
            add_edge=lambda x, _src, _dst, w: (x[0], x[1] + x[0] * w),
        )
        rr.add_edge(0, 1, 2)
        rr.add_edge(1, 2, 3)
        rr.add_edge(1, 3, 5)

        self.assertEqual([x[1] for x in rr.solve()], [14, 10, 16, 20])

    def test_directional_edge_data(self):
        rr = Rerooting(
            2,
            identity="",
            merge=lambda a, b: a + b,
            add_vertex=lambda x, v: x + str(v),
            add_edge=lambda x, _src, _dst, label: x + label,
        )
        rr.add_edge(0, 1, "a", "b")

        self.assertEqual(rr.solve(), ["1b0", "0a1"])

    def test_random_unweighted_distance_sums_against_bfs(self):
        rng = random.Random(0)
        for n in range(1, 30):
            graph = [[] for _ in range(n)]
            rr = Rerooting(
                n,
                identity=(0, 0),
                merge=lambda a, b: (a[0] + b[0], a[1] + b[1]),
                add_vertex=lambda x, _v: (x[0] + 1, x[1]),
                add_edge=lambda x, _src, _dst, _data: (x[0], x[1] + x[0]),
            )
            for v in range(1, n):
                u = rng.randrange(v)
                graph[u].append(v)
                graph[v].append(u)
                rr.add_edge(u, v, None)

            expected = []
            for start in range(n):
                distance = [-1] * n
                distance[start] = 0
                queue = deque([start])
                while queue:
                    v = queue.popleft()
                    for to in graph[v]:
                        if distance[to] == -1:
                            distance[to] = distance[v] + 1
                            queue.append(to)
                expected.append(sum(distance))

            self.assertEqual([x[1] for x in rr.solve()], expected)

    def test_invalid_graph(self):
        rr = Rerooting(
            3,
            identity=0,
            merge=lambda a, b: a + b,
            add_vertex=lambda x, _v: x + 1,
            add_edge=lambda x, _src, _dst, _data: x,
        )
        rr.add_edge(0, 1, None)
        with self.assertRaisesRegex(ValueError, "tree"):
            rr.solve()


if __name__ == "__main__":
    unittest.main()
