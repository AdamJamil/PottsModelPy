from typing import List, TypeVar, Optional, Callable
from polynomial import Polynomial

from re_sum import *
from states import get_states


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
                tot += Polynomial.monomial(n_c)
            # mult_poly_scalar(tot, [n, n_c])
            # print(f"tot: {fmt_polynomial(tot)}, state: {x}")
            for dst in range(3):
                n_c = x[dst] - (src == dst)
                y = tuple(cnt - (i == src) + (i == dst) for i, cnt in enumerate(x))
                y = y[0], max(y[1], y[2]), min(y[1], y[2])
                # print(f"dst: {dst}, y: {y}")
                idx_y = states.index(y)
                A[idx_x][idx_y] += RationalFunc(Polynomial.monomial(n_c) * Rational(x[src], n), cp(tot))

    return A


def evaluate_matrix_at_rational(A: List[List[RESum]], lambd: Rational):
    return [[f(lambd) for f in row] for row in A]


T = TypeVar("T")
import time


def mult_matrix(A: List[List[T]], B: List[List[T]], add_id: Optional[T] = None):
    add_id = 0 if add_id is None else add_id
    n, p, m = len(A), len(A[0]), len(B[0])
    C = [[cp(add_id) for _ in range(n)] for _ in range(m)]
    mul_time = 0
    add_time = 0
    for i in range(n):
        for j in range(p):
            for k in range(m):
                start = time.perf_counter_ns()
                res = A[i][j] * B[j][k]
                mul_time += time.perf_counter_ns() - start
                start = time.perf_counter_ns()
                C[i][k] += res
                add_time += time.perf_counter_ns() - start
    print(f" > mat mul time: {mul_time  / 1_000_000_000}")
    print(f" > mat add time: {add_time  / 1_000_000_000}")
    return C
