from ..mylib.argument_sort import argument_compare, argument_sort, argument_sort_key


def main():
    points = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    original = points.copy()
    assert argument_sort(points) == [(1, 0), (0, 1), (-1, 0), (0, -1)]
    assert points == original

    same_line = [(4, 2), (1, 2), (3, 2), (2, 2), (0, 2)]
    assert argument_sort(same_line, center=(2, 2)) == [
        (2, 2),
        (3, 2),
        (4, 2),
        (1, 2),
        (0, 2),
    ]

    cardinal = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    assert argument_sort(cardinal, start=(0, 1)) == [
        (0, 1),
        (-1, 0),
        (0, -1),
        (1, 0),
    ]
    assert argument_sort(cardinal, start=(0, 1), clockwise=True) == [
        (0, 1),
        (1, 0),
        (0, -1),
        (-1, 0),
    ]

    in_place = [(0, -1), (0, 1), (1, 0)]
    in_place.sort(key=argument_sort_key())
    assert in_place == [(1, 0), (0, 1), (0, -1)]
    assert argument_compare((1, 0), (0, 1)) < 0
    assert argument_compare((2, 0), (2, 0)) == 0

    # 積が64bit整数の範囲に収まる大きな座標でも浮動小数点を使わない。
    large = 10**9
    large_points = [(large, 1), (large, 0), (large, -1)]
    assert argument_sort(large_points) == [
        (large, 0),
        (large, 1),
        (large, -1),
    ]

    print("ok")


if __name__ == "__main__":
    main()
