"""Codon向けの整数座標の偏角ソート。

``atan2`` を使わず、半平面の判定と外積だけで順序を決める。既定では
``center`` から見た正の x 軸を始点として、反時計回りに一周する順序になる。

同じ半直線上にある点は中心に近い順、中心と一致する点は常に先頭に置く。
点の型は Codon の静的型付けに合わせて ``tuple[int, int]`` に限定している。

典型的な使い方::

    points = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    ordered = argument_sort(points)
    # [(1, 0), (0, 1), (-1, 0), (0, -1)]

中心、開始方向、回転方向も変更できる::

    ordered = argument_sort(points, (10, 20), (0, 1), True)

既存のリストをその場で並べ替える場合は ``argument_sort_key`` を使う::

    points.sort(key=argument_sort_key((0, 0), (1, 0), False))

N 点のソート時間は O(N log N)、追加メモリは O(N)。Codon の ``int`` は
固定幅なので、外積・内積・距離の二乗が整数の表現範囲を超えないこと。
"""

from .sort import cmp_to_key


def _make_compare(
    center: tuple[int, int],
    start: tuple[int, int],
    clockwise: bool,
):
    cx, cy = center
    sx, sy = start
    if sx == 0 and sy == 0:
        raise ValueError("start direction must be non-zero")

    def compare(a: tuple[int, int], b: tuple[int, int]) -> int:
        ax, ay = a[0] - cx, a[1] - cy
        bx, by = b[0] - cx, b[1] - cy
        a_is_center = ax == 0 and ay == 0
        b_is_center = bx == 0 and by == 0
        if a_is_center or b_is_center:
            if a_is_center and b_is_center:
                return 0
            return -1 if a_is_center else 1

        # start から指定方向に測った角度が [0, pi) なら前半、[pi, 2pi) なら後半。
        cross_start_a = sx * ay - sy * ax
        cross_start_b = sx * by - sy * bx
        if clockwise:
            cross_start_a = -cross_start_a
            cross_start_b = -cross_start_b
        dot_start_a = sx * ax + sy * ay
        dot_start_b = sx * bx + sy * by
        half_a = 0 if cross_start_a > 0 or (cross_start_a == 0 and dot_start_a > 0) else 1
        half_b = 0 if cross_start_b > 0 or (cross_start_b == 0 and dot_start_b > 0) else 1
        if half_a != half_b:
            return -1 if half_a < half_b else 1

        cross_ab = ax * by - ay * bx
        if clockwise:
            cross_ab = -cross_ab
        if cross_ab != 0:
            return -1 if cross_ab > 0 else 1

        distance_a = ax * ax + ay * ay
        distance_b = bx * bx + by * by
        if distance_a < distance_b:
            return -1
        if distance_a > distance_b:
            return 1
        return 0

    return compare


def argument_compare(
    a: tuple[int, int],
    b: tuple[int, int],
    center: tuple[int, int] = (0, 0),
    start: tuple[int, int] = (1, 0),
    clockwise: bool = False,
) -> int:
    """2点の偏角順を比較し、a < b なら負、等価なら0、a > b なら正を返す。"""
    return _make_compare(center, start, clockwise)(a, b)


def argument_sort_key(
    center: tuple[int, int] = (0, 0),
    start: tuple[int, int] = (1, 0),
    clockwise: bool = False,
):
    """``list.sort`` に渡せる偏角ソート用キーを返す。

    例: ``points.sort(key=argument_sort_key(clockwise=True))``
    """
    return cmp_to_key(_make_compare(center, start, clockwise))


def argument_sort(
    points: list[tuple[int, int]],
    center: tuple[int, int] = (0, 0),
    start: tuple[int, int] = (1, 0),
    clockwise: bool = False,
) -> list[tuple[int, int]]:
    """点列を偏角順に並べた新しいリストを返す。

    Args:
        points: ``(x, y)`` 形式の整数座標のリスト。
        center: 偏角を測る中心。既定値は原点 ``(0, 0)``。
        start: 角度0とみなす非零の方向ベクトル。既定値は ``(1, 0)``。
        clockwise: ``False`` なら反時計回り、``True`` なら時計回り。

    入力リストは変更しない。戻り値は偏角、中心からの距離の順に並ぶ。
    """
    result = points.copy()
    result.sort(key=argument_sort_key(center, start, clockwise))
    return result
