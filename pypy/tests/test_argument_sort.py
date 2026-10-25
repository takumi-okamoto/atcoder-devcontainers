import math
import random
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mylib.argument_sort import argument_compare, argument_sort, argument_sort_key


class ArgumentSortTest(unittest.TestCase):
    def test_cardinal_directions_and_input_is_not_modified(self):
        points = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        original = points.copy()

        self.assertEqual(
            argument_sort(points),
            [(1, 0), (0, 1), (-1, 0), (0, -1)],
        )
        self.assertEqual(points, original)

    def test_center_first_then_distance_on_same_ray(self):
        points = [(4, 2), (1, 2), (3, 2), (2, 2), (0, 2)]
        self.assertEqual(
            argument_sort(points, center=(2, 2)),
            [(2, 2), (3, 2), (4, 2), (1, 2), (0, 2)],
        )

    def test_custom_start_and_clockwise(self):
        points = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.assertEqual(
            argument_sort(points, start=(0, 1)),
            [(0, 1), (-1, 0), (0, -1), (1, 0)],
        )
        self.assertEqual(
            argument_sort(points, start=(0, 1), clockwise=True),
            [(0, 1), (1, 0), (0, -1), (-1, 0)],
        )

    def test_sort_key_and_compare(self):
        points = [(0, -1), (0, 1), (1, 0)]
        points.sort(key=argument_sort_key())
        self.assertEqual(points, [(1, 0), (0, 1), (0, -1)])
        self.assertLess(argument_compare((1, 0), (0, 1)), 0)
        self.assertEqual(argument_compare((2, 0), (2, 0)), 0)

    def test_large_integer_coordinates(self):
        huge = 10**100
        points = [(huge, 1), (huge, 0), (huge, -1)]
        self.assertEqual(
            argument_sort(points),
            [(huge, 0), (huge, 1), (huge, -1)],
        )

    def test_random_points_against_atan2(self):
        rng = random.Random(0)
        for _ in range(100):
            points = {
                (rng.randint(-20, 20), rng.randint(-20, 20)) for _ in range(30)
            }
            expected = sorted(
                points,
                key=lambda p: (
                    -1.0 if p == (0, 0) else math.atan2(p[1], p[0]) % math.tau,
                    p[0] * p[0] + p[1] * p[1],
                ),
            )
            self.assertEqual(argument_sort(points), expected)

    def test_invalid_arguments(self):
        with self.assertRaisesRegex(ValueError, "non-zero"):
            argument_sort([(1, 0)], start=(0, 0))
        with self.assertRaisesRegex(ValueError, "two coordinates"):
            argument_sort([(1, 0)], center=(0, 0, 0))
        with self.assertRaisesRegex(ValueError, "two coordinates"):
            argument_sort([(1, 0, 2)])


if __name__ == "__main__":
    unittest.main()
