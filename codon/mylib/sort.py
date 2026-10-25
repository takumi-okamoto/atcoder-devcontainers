# Comparator-based sorting helpers for Codon.
#
# `cmp(a, b)` follows the same convention as Python 2's cmp and
# functools.cmp_to_key: negative if a < b, zero if a == b, positive if a > b.
# Codon に cmp_to_key がないの許せない...!!!


def sort[T](a: list[T], cmp, reverse: bool = False):
    """Sort ``a`` in place with a three-way comparator.

    The implementation is a stable bottom-up merge sort. It takes O(n log n)
    time and O(n) additional memory, and avoids recursion and list slicing.
    """
    n = len(a)
    if n < 2:
        return

    src = a.copy()
    dst = a.copy()
    width = 1

    while width < n:
        begin = 0
        while begin < n:
            mid = min(begin + width, n)
            end = min(begin + 2 * width, n)
            i = begin
            j = mid
            k = begin

            while i < mid and j < end:
                order = cmp(src[j], src[i])
                take_right = order > 0 if reverse else order < 0
                if take_right:
                    dst[k] = src[j]
                    j += 1
                else:
                    # Taking from the left on equality makes the sort stable.
                    dst[k] = src[i]
                    i += 1
                k += 1

            while i < mid:
                dst[k] = src[i]
                i += 1
                k += 1

            while j < end:
                dst[k] = src[j]
                j += 1
                k += 1

            begin = end

        src, dst = dst, src
        width *= 2

    for i in range(n):
        a[i] = src[i]


@tuple
class _CmpKey[T, C]:
    obj: T
    cmp: C

    def __lt__(self, other):
        return self.cmp(self.obj, other.obj) < 0

    def __le__(self, other):
        return self.cmp(self.obj, other.obj) <= 0

    def __eq__(self, other):
        return self.cmp(self.obj, other.obj) == 0

    def __ne__(self, other):
        return self.cmp(self.obj, other.obj) != 0

    def __gt__(self, other):
        return self.cmp(self.obj, other.obj) > 0

    def __ge__(self, other):
        return self.cmp(self.obj, other.obj) >= 0


def cmp_to_key(cmp):
    """Convert a three-way comparator into a key function for list.sort."""
    return lambda obj: _CmpKey(obj, cmp)
