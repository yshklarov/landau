#!/usr/bin/env python3

# Computes the values of Landau's function.

import itertools
import functools
from operator import mul
from multiprocessing import Pool
import math

def is_prime(n):
    if n <= 1:
        return False
    for k in range(2, int(math.sqrt(n)+0.5) + 1):
        if n % k == 0:
            return False
    return True

def primes():
    return filter(is_prime, itertools.count(2))

def capped_product(n, *args):
    # Like a cartesian product, but allows skipping a set, and
    # returns only elements whose sum is below n.
    # capped_product(6, [1, 2], [5]) == [[], [5], [1], [1, 5], [2]]
    if (n < 0):
        return []
    if len(args) == 0:
        return [[]]
    # Skip the first pool
    result = capped_product(n, *args[1:])
    for i in args[0]:
        result += map(lambda rest: [i] + rest,
                      capped_product(n - i, *args[1:]))
    return result

def gen_candidates(n):
    def powers_until(p, max):
        # We skip 1's, they are useless.
        return list(
            itertools.takewhile(lambda k: k <= n,
                                map(lambda j: p**j, itertools.count(1))))
    small_primes = itertools.takewhile(lambda p: p <= n, primes())
    prime_powers_grid = [powers_until(p, n) for p in small_primes]
    for valid_list in capped_product(n, *prime_powers_grid):
        yield tuple(filter(lambda x: x != 0, valid_list))

# Compute the highest-order element of the symmetric group S_n.
def highest_order_permutation(n):
    best_order = 0
    best_cycle_lengths = ()
    for cycle_lengths in gen_candidates(n):
        order = functools.reduce(mul, cycle_lengths, 1)
        if order > best_order:
            best_order = order
            best_cycle_lengths = cycle_lengths
            # Best so far
            #print(str(order) + ": " + str(cycle_lengths))
    return (n, best_order, best_cycle_lengths)

if __name__ == '__main__':
    with Pool(processes=8) as pool:
        bests = pool.imap(highest_order_permutation, itertools.count(1))
        for (n, order, cycle_lengths) in bests:
            print("g({}) = {}\t{}".format(n, order, cycle_lengths), flush=True)
