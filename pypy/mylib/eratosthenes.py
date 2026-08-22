def sieve_of_eratosthenes(limit: int) -> tuple[list[int], list[int]]:
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    min_factor = [-1] * (limit + 1)
    for start in range(2, int(limit**0.5) + 1):
        if sieve[start]:
            for i in range(start * start, limit + 1, start):
                sieve[i] = False
                if min_factor[i] == -1:
                    min_factor[i] = start

    return [num for num, is_prime in enumerate(sieve) if is_prime], min_factor
