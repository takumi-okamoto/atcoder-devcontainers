# ==============================================
# ローリングハッシュ, Trie木, Suffix Array 実装
# 競技プログラミング向けユーティリティ
# ==============================================

# =====================
# ローリングハッシュ
# =====================
# 基数 base は通常 911 や 1007 などの素数を選ぶ。
# mod は 2^61 - 1 や 10**9+7 など大きな素数がよい。
# 異なる base, mod のペアを複数用意することで衝突を回避できる。


class RollingHash:
    def __init__(self, s: str, base: int = 1007, mod: int = 10**9 + 7):
        """
        s: 対象文字列
        base: 基数（文字を数値に変換する際の重み）
        mod: ハッシュの法（大きな素数）
        """
        self.mod: int = mod
        self.base: int = base
        self.hash: list[int] = [0] * (len(s) + 1)
        self.power: list[int] = [1] * (len(s) + 1)

        for i in range(len(s)):
            self.hash[i + 1] = (self.hash[i] * base + ord(s[i])) % mod
            self.power[i + 1] = self.power[i] * base % mod

    def get(self, l: int, r: int) -> int:
        """
        s[l:r] のハッシュ値を返す（半開区間）
        """
        return (self.hash[r] - self.hash[l] * self.power[r - l]) % self.mod

    def connect(self, h1: int, h2: int, h2_len: int) -> int:
        """
        ハッシュ h1 と h2 を連結した結果のハッシュを返す。
        h1: 前半文字列のハッシュ
        h2: 後半文字列のハッシュ
        h2_len: h2 の長さ
        """
        return (h1 * self.power[h2_len] + h2) % self.mod


# ============
# Trie 木
# ============
# 接頭辞検索や単語の存在判定に便利


class TrieNode:
    def __init__(self):
        self.children = {}  # 各文字に対する子ノード
        self.is_end_of_word = False  # 単語の終端かどうか


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        """
        単語を Trie に挿入
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        """
        完全一致で単語を検索
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix):
        """
        接頭辞検索
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def collect_words(self, prefix=""):
        """
        指定した prefix 以下のすべての単語を収集
        """
        results = []

        def dfs(node, path):
            if node.is_end_of_word:
                results.append(prefix + path)
            for c in node.children:
                dfs(node.children[c], path + c)

        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        dfs(node, "")
        return results


# ======================
# Suffix Array (Manber-Myers)
# ======================
# 文字列のすべての接尾辞を辞書順に並べた配列
# LCP 配列などと併用して文字列問題に対応


def build_suffix_array(s):
    """
    文字列 s に対する Suffix Array を構築
    """
    n = len(s)
    k = 1
    rank = [ord(c) for c in s]  # 各文字の初期ランク（ASCII）
    tmp = [0] * n
    sa = list(range(n))  # suffix の開始インデックス配列

    while True:
        # k文字先までのランクで比較してソート
        sa.sort(key=lambda x: (rank[x], rank[x + k] if x + k < n else -1))

        # 一時ランクの更新
        tmp[sa[0]] = 0
        for i in range(1, n):
            prev = (rank[sa[i - 1]], rank[sa[i - 1] + k] if sa[i - 1] + k < n else -1)
            curr = (rank[sa[i]], rank[sa[i] + k] if sa[i] + k < n else -1)
            tmp[sa[i]] = tmp[sa[i - 1]] + (prev != curr)

        rank = tmp[:]
        if rank[sa[-1]] == n - 1:
            break
        k <<= 1  # 比較文字数を倍増

    return sa


# ======================
# Z-Algorithm
# ======================
# Z[i] は S と S[i:] の最長共通接頭辞の長さを表す。
# O(N) 時間で前処理可能で、文字列探索（パターンマッチング）に便利。


def z_algorithm(s):
    """
    Z-Algorithm を用いて文字列 s の Z 配列を構築
    Z[i]: s[0:] と s[i:] の最長共通接頭辞の長さ
    計算量: O(|s|)
    """
    n = len(s)
    Z = [0] * n
    Z[0] = n  # 自身との一致長は文字列長
    l = r = 0  # [l, r) は現在の Z-box

    for i in range(1, n):
        if i <= r:
            Z[i] = min(r - i, Z[i - l])  # Z-box を利用できる場合
        while i + Z[i] < n and s[Z[i]] == s[i + Z[i]]:
            Z[i] += 1
        if i + Z[i] > r:
            l, r = i, i + Z[i]  # 新しい Z-box を更新

    return Z


# 例:
# s = "ababcab"
# -> z_algorithm(s) = [7, 0, 2, 0, 0, 2, 0]
# （s[2:] = "abcab" と s の共通接頭辞は "ab" → 長さ2）
