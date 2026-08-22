def iscolinear(A: list[tuple[int, int]]):
    if len(A) <= 2:
        return True
    x0 = A[0][0]
    y0 = A[0][1]

    x1 = A[1][0]
    y1 = A[1][1]

    dx = x1 - x0
    dy = y1 - y0

    for ai in A[2:]:
        x = ai[0]
        y = ai[1]
        if dx * (y - y0) != dy * (x - x0):
            return False

    return True
