from typing import Iterator

import sortedcontainers


class ManagedIntervals:
    """
    互いに素な区間 [l, r) の集合を管理するクラスです。

    このクラスは、整数の集合を、互いに素な区間のリストとして効率的に管理します。
    例えば、{1, 2, 3, 7, 8} という集合は、`[1, 4)` と `[7, 9)` という2つの区間として
    表現されます。

    内部データ構造として `sortedcontainers.Sortedlist` を利用し、
    区間の左端 `l` でソートされた状態を保つことで、各種操作を高速に実行します。
    区間はすべて右半開区間 `[l, r)` (l <= x < r) として扱われます。

    主な機能:
    - `add(l, r)`: 区間 `[l, r)` を追加します。既存の区間と重なる、または隣接する場合、
      それらは自動的に1つの大きな区間にマージされます。
    - `remove(l, r)`: 区間 `[l, r)` を削除します。この操作により、既存の区間が
      短くなったり、2つに分割されたり、完全に削除されたりすることがあります。
    - `__contains__(x)`: ある整数 `x` がいずれかの区間に含まれているかを $O(\log N)$ で
      判定します。
    - `get_interval(x)`: ある整数 `x` を含む区間 `[l, r)` を $O(\log N)$ で取得します。
    - `total_length`: 管理下の全区間の長さの合計を $O(1)$ で取得します。

    使用例:
    ```python
    intervals = ManagedIntervals()
    intervals.add(1, 5)        # 管理下の区間: {[1, 5)}
    intervals.add(8, 10)       # 管理下の区間: {[1, 5), [8, 10)}
    intervals.add(4, 9)        # [1, 5), [8, 10) と [4, 9) がマージされ {[1, 10)} となる

    print(intervals)           # -> ManagedIntervals([(1, 10)])
    print(3 in intervals)      # -> True
    print(6 in intervals)      # -> True
    print(10 in intervals)     # -> False (右半開区間 [1, 10) のため)

    intervals.remove(3, 7)     # [1, 10) が分割され {[1, 3), [7, 10)} となる
    print(intervals)           # -> ManagedIntervals([(1, 3), (7, 10)])
    print(intervals.total_length) # -> (3 - 1) + (10 - 7) = 5
    ```
    """

    def __init__(self) -> None:
        """`ManagedIntervals` のインスタンスを初期化します。"""
        # 区間 (l, r) をタプルとして格納するSortedlist。l (タプルの第一要素) でソートされる。
        self._intervals: sortedcontainers.Sortedlist[tuple[int, int]] = (
            sortedcontainers.Sortedlist()
        )
        # 全区間の長さの合計を保持する。O(1)でのアクセスを可能にするため。
        self._total_length: int = 0

    def add(self, l: int, r: int) -> None:
        """
        区間 [l, r) を追加します。

        既存の区間と重なる、または隣接する場合、それらは1つの区間にマージされます。
        計算量: O(k * log N)。ここで N は管理下の区間数、k はこの操作でマージされる区間数。

        Args:
            l (int): 追加する区間の左端（を含む）。
            r (int): 追加する区間の右端（を含まない）。
        """
        if l >= r:
            return

        # --- ステップ1: マージ対象となる区間を探索し、マージ後の範囲を決定 ---
        to_remove: list[tuple[int, int]] = []
        merged_l, merged_r = l, r

        # 探索開始インデックスを効率的に見つける
        # new_l と重なる可能性のある最初の区間から探索を始める
        # (l, +inf) より大きい最初の要素のインデックスを探し、その一つ手前からが候補
        idx = self._intervals.bisect_right((l, float("inf")))
        if idx > 0:
            idx -= 1

        # [l, r) と重なるか隣接する区間 (L, R) を全て見つける
        # 条件: not (R < l or L > r) <=> R >= l and L <= r
        for i in range(idx, len(self._intervals)):
            L, R = self._intervals[i]

            # L が merged_r より大きい場合、それ以降の区間はマージ対象外
            if L > merged_r:
                break

            # R が merged_l より小さい場合、この区間はマージ対象外
            if R < merged_l:
                continue

            # 重なるか隣接しているため、マージ対象に加える
            to_remove.append((L, R))
            merged_l = min(merged_l, L)
            merged_r = max(merged_r, R)

        # --- ステップ2: 既存の区間を削除し、新しいマージ済み区間を追加 ---
        if to_remove:
            old_len = sum(R - L for L, R in to_remove)
            for interval in to_remove:
                self._intervals.remove(interval)
            self._total_length -= old_len

        self._intervals.add((merged_l, merged_r))
        self._total_length += merged_r - merged_l

    def remove(self, l: int, r: int) -> None:
        """
        区間 [l, r) を削除します。

        この操作により、既存の区間が短くなったり、2つに分割されたり、
        完全に削除されたりする可能性があります。
        計算量: O(k * log N)。ここで N は管理下の区間数、k はこの操作で影響を受ける区間数。

        Args:
            l (int): 削除する区間の左端（を含む）。
            r (int): 削除する区間の右端（を含まない）。
        """
        if l >= r:
            return

        # --- ステップ1: 削除対象の区間と重なる既存区間を特定 ---
        to_add: list[tuple[int, int]] = []
        to_remove: list[tuple[int, int]] = []

        # 探索開始インデックスを効率的に見つける
        # l と重なる可能性のある最初の区間から探索を始める
        idx = self._intervals.bisect_right((l, float("inf")))
        if idx > 0:
            idx -= 1

        # [l, r) と重なる区間 (L, R) を全て見つける
        # 条件: L < r and R > l
        for i in range(idx, len(self._intervals)):
            L, R = self._intervals[i]

            # L が r 以上の場合、それ以降の区間は重ならない
            if L >= r:
                break

            # R が l 以下の場合、この区間は重ならない
            if R <= l:
                continue

            # 重なっている区間を削除対象リストへ
            to_remove.append((L, R))

            # --- ステップ2: 区間の分割・縮小後の新しい区間を計算 ---
            # 元の区間の左側が残る場合
            if L < l:
                to_add.append((L, l))
            # 元の区間の右側が残る場合
            if r < R:
                to_add.append((r, R))

        # --- ステップ3: 既存の区間を削除し、新しい区間を追加 ---
        if to_remove:
            old_len = sum(R - L for L, R in to_remove)
            new_len = sum(R - L for L, R in to_add)

            for interval in to_remove:
                self._intervals.remove(interval)

            for interval in to_add:
                self._intervals.add(interval)

            self._total_length += new_len - old_len

    def get_interval(self, x: int) -> tuple[int, int] | None:
        """
        指定された整数 x を含む区間 [l, r) を返します。

        x がどの区間にも含まれていない場合は `None` を返します。
        計算量: O(log N)

        Args:
            x (int): 検索する整数。

        Returns:
            Optional[tuple[int, int]]: x を含む区間 `(l, r)`、または `None`。
        """
        # (x, +inf) より大きい最初の要素のインデックスを探す
        idx = self._intervals.bisect_right((x, float("inf")))

        # idx が 0 の場合、x より小さい l を持つ区間は存在しない
        if idx == 0:
            return None

        # 候補となる区間は一つ前のインデックス
        l, r = self._intervals[idx - 1]

        # x がその区間内に含まれるかチェック (l <= x < r)
        # l <= x は bisect_right の性質から保証されるため、x < r のみチェック
        if x < r:
            return (l, r)

        return None

    def __contains__(self, x: int) -> bool:
        """
        指定された整数 x がいずれかの区間に含まれているかを判定します。

        `get_interval(x)` を利用した糖衣構文です。
        計算量: O(log N)

        Args:
            x (int): 判定する整数。

        Returns:
            bool: x がいずれかの区間に含まれていれば `True`、そうでなければ `False`。
        """
        return self.get_interval(x) is not None

    @property
    def total_length(self) -> int:
        """
        管理されている全ての区間の長さの合計を返します。
        計算量: O(1)

        Returns:
            int: 全区間の長さの合計。
        """
        return self._total_length

    def to_list(self) -> list[tuple[int, int]]:
        """
        管理されている全ての区間をソートされたリストとして返します。
        計算量: O(N)

        Returns:
            list[tuple[int, int]]: 区間 `(l, r)` のリスト。
        """
        return list(self._intervals)

    def __iter__(self) -> Iterator[tuple[int, int]]:
        """管理下の全ての区間をイテレートするためのイテレータを返します。"""
        return iter(self._intervals)

    def __len__(self) -> int:
        """管理されている区間の数を返します。"""
        return len(self._intervals)

    def __bool__(self) -> bool:
        """管理下の区間が1つ以上存在するかを返します。"""
        return len(self._intervals) > 0

    def __str__(self) -> str:
        """`ManagedIntervals` オブジェクトの読みやすい文字列表現を返します。"""
        return f"ManagedIntervals({self.to_list()})"

    def __repr__(self) -> str:
        """`ManagedIntervals` オブジェクトの明確な文字列表現を返します。"""
        return f"ManagedIntervals({self.to_list()})"
