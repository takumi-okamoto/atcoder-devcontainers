import random
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mylib.persistent_segtree import PersistentSegmentTree


class PersistentSegmentTreeTest(unittest.TestCase):
    def test_versions_are_immutable_and_can_branch(self):
        seg = PersistentSegmentTree([1, 2, 3, 4], lambda a, b: a + b, 0)
        root0 = seg.root
        root1 = seg.set(root0, 1, 20)
        root2 = seg.set(root0, 2, 30)

        self.assertEqual(seg.all_prod(root0), 10)
        self.assertEqual(seg.all_prod(root1), 28)
        self.assertEqual(seg.all_prod(root2), 37)
        self.assertEqual(seg.get(root0, 1), 2)
        self.assertEqual(seg.get(root1, 1), 20)
        self.assertEqual(seg.get(root2, 1), 2)

    def test_non_commutative_operation_preserves_order(self):
        seg = PersistentSegmentTree(list("abcdef"), lambda a, b: a + b, "")
        root1 = seg.set(seg.root, 2, "X")

        self.assertEqual(seg.prod(seg.root, 1, 5), "bcde")
        self.assertEqual(seg.prod(root1, 1, 5), "bXde")
        self.assertEqual(seg.prod(root1, 3, 3), "")

    def test_identity_filled_tree_is_sparse(self):
        seg = PersistentSegmentTree(10**9, lambda a, b: a + b, 0)
        self.assertEqual(seg.node_count, 0)

        root1 = seg.set(seg.root, 123456789, 7)
        root2 = seg.set(root1, 987654321, 11)
        self.assertLessEqual(seg.node_count, 62)
        self.assertEqual(seg.prod(seg.root, 0, 10**9), 0)
        self.assertEqual(seg.prod(root1, 0, 10**9), 7)
        self.assertEqual(seg.prod(root2, 100000000, 900000000), 7)
        self.assertEqual(seg.prod(root2, 900000000, 10**9), 11)

    def test_random_branching_versions_against_lists(self):
        rng = random.Random(0)
        n = 31
        initial = [rng.randrange(-10, 11) for _ in range(n)]
        seg = PersistentSegmentTree(initial, lambda a, b: a + b, 0)
        roots = [seg.root]
        versions = [initial]

        for _ in range(300):
            base = rng.randrange(len(roots))
            index = rng.randrange(n)
            value = rng.randrange(-10, 11)
            current = versions[base].copy()
            current[index] = value
            roots.append(seg.set(roots[base], index, value))
            versions.append(current)

            version = rng.randrange(len(roots))
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            self.assertEqual(
                seg.prod(roots[version], left, right),
                sum(versions[version][left:right]),
            )

    def test_empty_tree_and_invalid_arguments(self):
        empty = PersistentSegmentTree([], lambda a, b: a + b, 0)
        self.assertEqual(empty.all_prod(empty.root), 0)
        self.assertEqual(empty.prod(empty.root, 0, 0), 0)
        with self.assertRaises(IndexError):
            empty.set(empty.root, 0, 1)

        seg = PersistentSegmentTree(3, max, -(10**18))
        with self.assertRaises(IndexError):
            seg.get(seg.root, -1)
        with self.assertRaises(IndexError):
            seg.prod(seg.root, 2, 1)
        with self.assertRaises(IndexError):
            seg.all_prod(10**9)
        with self.assertRaises(ValueError):
            PersistentSegmentTree(-1, max, -(10**18))


if __name__ == "__main__":
    unittest.main()
