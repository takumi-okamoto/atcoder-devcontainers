"""整数座標の点を偏角順にソートする。

``atan2`` を使わず、半平面の判定と外積だけで順序を決めるため、巨大な整数
座標でも浮動小数点誤差が生じない。既定では ``center`` から見た正の x 軸を
始点として、反時計回りに一周する順序になる。

同じ半直線上にある点は ``center`` に近い順に並ぶ。``center`` と一致する点は
偏角を持たないが、この実装では常に先頭に置く。同じ座標の点どうしには順序を
付けないため、Python の安定ソートによって入力中の順序が保たれる。

典型的な使い方::

    points = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    ordered = argument_sort(points)
    # [(1, 0), (0, 1), (-1, 0), (0, -1)]

中心や開始方向、回転方向も変更できる::

    ordered = argument_sort(
        points,
        center=(10, 20),
        start=(0, 1),       # 正の y 方向から開始
        clockwise=True,
    )

既存のリストをその場で並べ替えたい場合は ``argument_sort_key`` を使う::

    points.sort(key=argument_sort_key(center=(0, 0)))

N 点のソート時間は O(N log N)、ソート以外の追加メモリは O(N)。比較時の
四則演算が厳密であることを前提とするため、座標と開始方向には整数を使うこと。
"""

from functools import cmp_to_key
from typing import Callable, Iterable, Sequence, TypeVar


P = TypeVar("P", bound=Sequence[int])


def _make_compare(
    center: Sequence[int], start: Sequence[int], clockwise: bool
) -> Callable[[Sequence[int], Sequence[int]], int]:
    if len(center) != 2:
        raise ValueError("center must have exactly two coordinates")
    if len(start) != 2:
        raise ValueError("start must have exactly two coordinates")

    cx, cy = center
    sx, sy = start
    if sx == 0 and sy == 0:
        raise ValueError("start direction must be non-zero")

    def compare(a: Sequence[int], b: Sequence[int]) -> int:
        if len(a) != 2 or len(b) != 2:
            raise ValueError("each point must have exactly two coordinates")

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
        return (distance_a > distance_b) - (distance_a < distance_b)

    return compare


def argument_compare(
    a: Sequence[int],
    b: Sequence[int],
    *,
    center: Sequence[int] = (0, 0),
    start: Sequence[int] = (1, 0),
    clockwise: bool = False,
) -> int:
    """2点の偏角順を比較し、a < b なら負、等価なら0、a > b なら正を返す。

    単発の比較用。多数の点を並べる場合は、設定値の検証を一度だけ行う
    ``argument_sort`` または ``argument_sort_key`` を使う方が効率的である。
    """

    return _make_compare(center, start, clockwise)(a, b)


def argument_sort_key(
    *,
    center: Sequence[int] = (0, 0),
    start: Sequence[int] = (1, 0),
    clockwise: bool = False,
) -> Callable[[P], object]:
    """``list.sort`` や ``sorted`` に渡せる偏角ソート用キーを返す。

    例: ``points.sort(key=argument_sort_key(clockwise=True))``
    """

    key_type = cmp_to_key(_make_compare(center, start, clockwise))

    def key(point: P) -> object:
        # 要素が1つしかなく比較が発生しない場合にも入力を検証する。
        if len(point) != 2:
            raise ValueError("each point must have exactly two coordinates")
        return key_type(point)

    return key


def argument_sort(
    points: Iterable[P],
    *,
    center: Sequence[int] = (0, 0),
    start: Sequence[int] = (1, 0),
    clockwise: bool = False,
) -> list[P]:
    """点列を偏角順に並べた新しいリストを返す。

    Args:
        points: ``(x, y)`` 形式の整数座標の反復可能オブジェクト。
        center: 偏角を測る中心。既定値は原点 ``(0, 0)``。
        start: 角度0とみなす非零の方向ベクトル。既定値は ``(1, 0)``。
        clockwise: ``False`` なら反時計回り、``True`` なら時計回り。

    Returns:
        偏角、中心からの距離の順に並べた新しいリスト。入力は変更しない。

    Raises:
        ValueError: center、start、または点が2次元でない場合、あるいは
            start が零ベクトルの場合。
    """

    return sorted(points, key=argument_sort_key(
        center=center, start=start, clockwise=clockwise
    ))
