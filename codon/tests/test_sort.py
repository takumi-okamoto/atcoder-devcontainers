from ..mylib.sort import cmp_to_key, sort


def int_cmp(a: int, b: int) -> int:
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def first_cmp(a: tuple[int, int], b: tuple[int, int]) -> int:
    return int_cmp(a[0], b[0])


def pair_cmp(a: tuple[int, int], b: tuple[int, int]) -> int:
    order = int_cmp(a[1], b[1])
    if order != 0:
        return order
    return int_cmp(a[0], b[0])


def main():
    empty: list[int] = []
    sort(empty, int_cmp)
    assert empty == []

    one = [42]
    sort(one, int_cmp)
    assert one == [42]

    values = [5, -1, 3, 3, 0, -7, 5]
    sort(values, int_cmp)
    assert values == [-7, -1, 0, 3, 3, 5, 5]

    sort(values, int_cmp, reverse=True)
    assert values == [5, 5, 3, 3, 0, -1, -7]

    # Equal elements retain their input order in either direction.
    stable = [(2, 0), (1, 1), (2, 2), (1, 3), (3, 4)]
    sort(stable, first_cmp)
    assert stable == [(1, 1), (1, 3), (2, 0), (2, 2), (3, 4)]

    sort(stable, first_cmp, reverse=True)
    assert stable == [(3, 4), (2, 0), (2, 2), (1, 1), (1, 3)]

    by_key = [(1, 2), (0, 2), (3, 1), (4, 3)]
    by_key.sort(key=cmp_to_key(pair_cmp))
    assert by_key == [(3, 1), (0, 2), (1, 2), (4, 3)]

    key = cmp_to_key(int_cmp)
    assert key(1) < key(2)
    assert key(2) == key(2)
    assert key(3) > key(2)

    print("ok")


if __name__ == "__main__":
    main()
