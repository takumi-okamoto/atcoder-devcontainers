class Imos:
    """class for Imos method

    Attributes:
        data (list): data

    One can add values for an interval [l, r) in O(1) time and
    can get the value of each index in O(n) time after adding data
    (here, n is the length of data).

    One can use this class as follows:
        >>> data = [0]*10
        >>> imos = Imos(data)
        >>> imos.add(0, 3, 1)
        >>> imos.add(2, 7, 2)
        >>> imos.add(5, 8, 3)
        >>> imos.add(9, 10, 4)
        >>> imos.get()
        [1, 1, 3, 2, 2, 5, 5, 3, 0, 4]
    """

    def __init__(self, data: list) -> None:
        """Inits Imos with data"""
        data = data.copy()
        data.append(0)
        self.__difference = [data[i] - data[i - 1] for i in range(len(data) - 1)]

    def add(self, l: int, r: int, x: int | float) -> None:
        """
        adds x to the interval [l, r).
        calculation is done in O(1) time.
        Args:
            l (int): left index of the interval
            r (int): right index of the interval
            x (int|float): value to add
        """
        if l == r:
            return
        if r < l:
            raise ValueError("r must be larger than l")
        if not (0 <= l <= len(self.__difference) and 0 <= r <= len(self.__difference)):
            raise IndexError(f"l and r must be in [0, {len(self.__difference)}]")
        self.__difference[l] += x
        if 0 <= r < len(self.__difference):
            self.__difference[r] -= x

    def get(self) -> list[list[int | float]]:
        """
        Gets the value of each index.

        Calculation is done in O(len(data)) time.

        Returns:
            list: list of the value of each index
        """
        data = [self.__difference[0]]
        for i in range(1, len(self.__difference)):
            data.append(data[-1] + self.__difference[i])
        return data


class Imos2D:
    """class for Imos method in 2D

    Attributes:
        data (list): data

    One can add values for an interval [u, d) x [l, r) in O(1) time and
    can get the value of each index in O(n) time after adding data
    (here, n is the size of data).

    One can use this class as follows:
        >>> data = [[0]*10 for _ in range(10)]
        >>> imos = Imos2D(data)
        >>> imos.add(0, 3, 0, 3, 1)
        >>> imos.add(2, 7, 2, 7, 2)
        >>> imos.add(3, 8, 5, 8, 3)
        >>> imos.add(8, 10, 9, 10, 4)
        >>> imos.get()
        [[1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
         [1, 1, 3, 0, 0, 0, 0, 0, 0, 0],
         [1, 1, 3, 2, 2, 2, 2, 0, 0, 0],
         [0, 0, 2, 2, 2, 5, 5, 3, 3, 0],
         [0, 0, 2, 2, 2, 5, 5, 3, 3, 0],
         [0, 0, 2, 2, 2, 5, 5, 3, 3, 0],
         [0, 0, 0, 0, 0, 3, 3, 3, 3, 0],
         [0, 0, 0, 0, 0, 3, 3, 3, 3, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 4]]
    """

    def __init__(self, data):
        """Inits Imos2D with data"""
        self.__original_data = data
        self.__H = len(data)
        self.__W = len(data[0])
        self.__difference = [[0] * self.__W for _ in range(self.__H)]

    def add(self, u, d, l, r, x):
        """
        add x to the interval [u, d) x [l, r).

        Args:
            u (int): upper index of the interval
            d (int): down index of the interval
            l (int): left index of the interval
            r (int): right index of the interval
            x (Union[int, float]): value to add
        """

        if l == r or u == d:
            return
        if r < l:
            raise ValueError("r must be larger than l")
        if d < u:
            raise ValueError("d must be larger than u")
        if not (
            0 <= u <= self.__H
            and 0 <= d <= self.__H
            and 0 <= l <= self.__W
            and 0 <= r <= self.__W
        ):
            raise IndexError(f"u and d must be in [0, {self.__H} and \
                    l and r must be in [0, {self.__W}].")

        self.__difference[u][l] += x
        if r < self.__W:
            self.__difference[u][r] -= x
        if d < self.__H:
            self.__difference[d][l] -= x
        if r < self.__W and d < self.__H:
            self.__difference[d][r] += x

    def get(self):
        """
        Gets the value of each index.

        Calculation is done in O(len(data)) time.

        Returns:
            list: list of the value of each index
        """
        diff = [[0] * self.__W for _ in range(self.__H)]
        for i in range(self.__H):
            diff[i][0] = self.__difference[i][0]
            for j in range(1, self.__W):
                diff[i][j] = diff[i][j - 1] + self.__difference[i][j]
        for i in range(1, self.__H):
            for j in range(self.__W):
                diff[i][j] += diff[i - 1][j]
        data = [[0] * self.__W for _ in range(self.__H)]
        for i in range(self.__H):
            for j in range(self.__W):
                data[i][j] = self.__original_data[i][j] + diff[i][j]
        return data
