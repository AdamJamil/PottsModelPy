import random
from typing import Tuple, List
from copy import deepcopy as cp

from expression import *
from test import TestExpression

State = Tuple[int, int, int]


def is_partial_ordering(r: List[List[int]]) -> bool:
    n = len(r)
    reflexive = all(r[i][i] for i in range(n))
    antisymmetric = all(r[i][j] != r[j][i] for i in range(n) for j in range(n))
    transitive = all(not (r[i][j] and r[j][k]) or r[i][k] for i in range(n) for j in range(n) for k in range(n))
    return reflexive and antisymmetric and transitive


def get_max_partial_ordering(n: int) -> List[List[int]]:
    r = [[True] * n for _ in range(n)]
    while not is_partial_ordering(r):
        lambd = 1.000001 + random.random() * 10
        t = random.randint(1, 4)
        for x in range(n):
            for y in range(n):
                if r[x][y]:
                    ...


def get_states(n: int) -> List[State]:
    states = []
    for blue in range(0, n + 1):
        for stars in range(0, n + 1 - blue):
            daggers = n - blue - stars
            if daggers > stars:
                continue
            states.append((blue, stars, daggers))
    return [*reversed(sorted(states))]


def generate_transition_matrix(n: int) -> List[List[RESum]]:
    states = get_states(n)
    s = len(states)
    A = [[cp(zero_REsum) for _ in range(s)] for _ in range(s)]
    for idx_x, x in enumerate(states):
        for src in range(3):
            if not x[src]:
                continue
            tot = cp(zero_poly)
            for dst in range(3):
                n_c = x[dst] - (src == dst)
                add_poly(tot, monomial(n_c))
            # mult_poly_scalar(tot, [n, n_c])
            # print(f"tot: {fmt_polynomial(tot)}, state: {x}")
            for dst in range(3):
                n_c = x[dst] - (src == dst)
                y = tuple(cnt - (i == src) + (i == dst) for i, cnt in enumerate(x))
                y = y[0], max(y[1], y[2]), min(y[1], y[2])
                # print(f"dst: {dst}, y: {y}")
                idx_y = states.index(y)
                add_REsum(A[idx_x][idx_y], [(mult_poly_scalar(monomial(n_c), [x[src], n]), tot)])

    return A


def main():
    TestExpression()
    print(get_states(6))
    for row in generate_transition_matrix(6):
        print(" | ".join(fmt_REsum(f) for f in row))


if __name__ == "__main__":
    main()
