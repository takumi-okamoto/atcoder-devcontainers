"""全方位木 DP (rerooting DP) の汎用実装。

全方位木 DP は、木の各頂点をそれぞれ根にしたときの DP 値を、全頂点分
まとめて O(N) で求める手法である。この実装では、隣接部分木から届く値を
次の3段階で処理する。

1. ``merge(left, right)`` で複数の隣接部分木の値を結合する。
2. ``add_vertex(value, vertex)`` で現在の頂点の情報を加える。
3. ``add_edge(value, src, dst, edge_data)`` で辺 ``src -> dst`` を越える
   ときの変換を行う。

たとえば、辺の重みがすべて1の木で各根からの距離の総和を求める場合、
DP値を ``(頂点数, 距離の総和)`` とする。部分木を辺の向こう側へ渡す際に、
その部分木の全頂点の距離が1ずつ増えるため、次のように書ける。

    rr = Rerooting(
        n,
        identity=(0, 0),
        merge=lambda a, b: (a[0] + b[0], a[1] + b[1]),
        add_vertex=lambda x, _v: (x[0] + 1, x[1]),
        add_edge=lambda x, _src, _dst, _data: (x[0], x[1] + x[0]),
    )
    for u, v in edges:
        rr.add_edge(u, v, None)

    distance_sums = [distance_sum for _, distance_sum in rr.solve()]

``merge`` は結合則を満たし、``identity`` を左右の単位元として扱える必要が
ある。可換である必要はなく、値は ``add_edge`` で辺を追加した順、つまり
隣接リスト順に結合される。

``identity`` や各コールバックの引数をその場で変更すると、同じオブジェクトを
別の計算でも共有して結果が壊れることがある。リストなどをDP値に使う場合も、
コールバックは新しい値を返すようにすること。

計算量は O(N)、追加で使うメモリも O(N)。再帰は使用しないため、深い木でも
再帰上限を変更する必要はない。
"""

from typing import Callable, Generic, TypeVar


T = TypeVar("T")
E = TypeVar("E")
_SAME = object()


class Rerooting(Generic[T, E]):
    """全方位木 DP を構築するクラス。

    Args:
        n: 頂点数。頂点番号は 0 以上 n 未満。
        identity: ``merge`` の左右の単位元。コールバック内で変更しないこと。
        merge: 2つの隣接部分木の値を結合する関数。結合則を満たすこと。
        add_vertex: ``(結合済みの値, 頂点番号)`` を受け取り、現在の頂点を
            含めたDP値を返す関数。
        add_edge: ``(DP値, 出発頂点, 到着頂点, 辺情報)`` を受け取り、値が
            有向辺を越えた後の値を返す関数。

    ``solve()[v]`` は、木を頂点 ``v`` を根として見たときの DP 値になる。
    辺は構築後に ``add_edge`` で n - 1 本追加してから ``solve`` を呼ぶ。

    ``solve`` の開始根は計算過程だけに使われ、戻り値の意味や並び順には
    影響しない。
    """

    def __init__(
        self,
        n: int,
        identity: T,
        merge: Callable[[T, T], T],
        add_vertex: Callable[[T, int], T],
        add_edge: Callable[[T, int, int, E], T],
    ) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self.n = n
        self.identity = identity
        self.merge = merge
        self.add_vertex = add_vertex
        self._add_edge = add_edge
        # 各要素は (行き先, 逆向きの辺の隣接リスト内インデックス, 辺情報)。
        self.graph: list[list[tuple[int, int, E]]] = [[] for _ in range(n)]
        self._edge_count = 0

    def add_edge(self, u: int, v: int, data_uv: E, data_vu=_SAME) -> None:
        """無向辺を追加する。

        ``data_uv`` は u -> v、``data_vu`` は v -> u で利用される。
        ``data_vu`` を省略すると両方向で ``data_uv`` を使う。

        無向の重み付き木なら ``add_edge(u, v, weight)``、辺情報を使わない
        場合は ``add_edge(u, v, None)`` とする。方向でコストなどが異なる
        場合は ``add_edge(u, v, u_to_v, v_to_u)`` と指定できる。

        Args:
            u: 辺の一方の端点。
            v: 辺のもう一方の端点。
            data_uv: u から v へ値を渡す際に ``add_edge`` へ渡す辺情報。
            data_vu: v から u へ値を渡す際の辺情報。省略時は data_uv。

        Raises:
            ValueError: 端点が範囲外、または自己ループである場合。
        """
        if not (0 <= u < self.n and 0 <= v < self.n):
            raise ValueError("vertex is out of range")
        if u == v:
            raise ValueError("self-loops are not allowed")
        if data_vu is _SAME:
            data_vu = data_uv

        ui = len(self.graph[u])
        vi = len(self.graph[v])
        self.graph[u].append((v, vi, data_uv))
        self.graph[v].append((u, ui, data_vu))
        self._edge_count += 1

    def solve(self, root: int = 0) -> list[T]:
        """全頂点をそれぞれ根とした DP 値を返す。

        Args:
            root: 内部の2回の走査で最初に根とする頂点。計算結果そのものは
                root に依存しないため、通常は既定値の0でよい。

        Returns:
            長さ n のリスト。戻り値の v 番目は、v を根とした木全体の
            DP値。n が0なら空リストを返す。

        Raises:
            ValueError: root が範囲外、辺数が n - 1 でない、グラフが連結で
                ない、または閉路を含む場合。

        同じ木とコールバックに対して複数回呼び出すこともできる。
        """
        if self.n == 0:
            if root != 0:
                raise ValueError("root is out of range")
            return []
        if not 0 <= root < self.n:
            raise ValueError("root is out of range")
        if self._edge_count != self.n - 1:
            raise ValueError("graph must be a tree")

        parent = [-2] * self.n
        parent_edge = [-1] * self.n
        parent[root] = -1
        order = [root]

        for v in order:
            for to, reverse_index, _ in self.graph[v]:
                if to == parent[v]:
                    continue
                if parent[to] != -2:
                    raise ValueError("graph must be a tree")
                parent[to] = v
                parent_edge[to] = reverse_index
                order.append(to)

        if len(order) != self.n:
            raise ValueError("graph must be connected")

        # incoming[v][i] は graph[v][i] の隣接頂点から v に届く値。
        incoming: list[list[T]] = [
            [self.identity for _ in edges] for edges in self.graph
        ]

        # 子から親へ値を伝える。
        for v in reversed(order[1:]):
            merged = self.identity
            skip = parent_edge[v]
            for i, value in enumerate(incoming[v]):
                if i != skip:
                    merged = self.merge(merged, value)
            value = self.add_vertex(merged, v)

            to, reverse_index, data = self.graph[v][skip]
            incoming[to][reverse_index] = self._add_edge(value, v, to, data)

        # 親から子へ値を伝える。各辺を除いた結合は累積積で O(1) に求める。
        answer: list[T] = [self.identity for _ in range(self.n)]
        for v in order:
            degree = len(self.graph[v])
            prefix = [self.identity] * (degree + 1)
            suffix = [self.identity] * (degree + 1)
            for i in range(degree):
                prefix[i + 1] = self.merge(prefix[i], incoming[v][i])
            for i in range(degree - 1, -1, -1):
                suffix[i] = self.merge(incoming[v][i], suffix[i + 1])

            answer[v] = self.add_vertex(prefix[degree], v)

            for i, (to, reverse_index, data) in enumerate(self.graph[v]):
                if to == parent[v]:
                    continue
                without_to = self.merge(prefix[i], suffix[i + 1])
                value = self.add_vertex(without_to, v)
                incoming[to][reverse_index] = self._add_edge(value, v, to, data)

        return answer
