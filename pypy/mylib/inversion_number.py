from atcoder.fenwicktree import FenwickTree


def inversion_number(a: list[int]):
    """
    a の転倒数を求める

    a の転倒数は、i < j かつ a[i] > a[j] となる (i, j) の組の数

    つまり, $\\sum_{j=0}^{n-1} \\sum_{i < j} [a[i] > a[j]]$ を求める

    このためには、各j について、a[i] > a[j] となる i < j の個数を求めればよい

    """
    n = max(a) + 1
    ft = FenwickTree(n)
    inv_count = 0
    for i in range(n):
        inv_count += i - ft.sum(0, a[i] + 1)
        ft.add(a[i], 1)
    return inv_count
