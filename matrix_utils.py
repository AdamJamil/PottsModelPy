from typing import List, TypeVar, Optional, Callable

from expression import *
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


def evaluate_matrix_at_rational(A: List[List[RESum]], lambd: Rational):
    return [[evaluate_REsum_at_rat(f, lambd) for f in row] for row in A]


T = TypeVar("T")


def mult_matrix(A: List[List[T]], B: List[List[T]], add: Optional[Callable[[T, T], T]] = None,
                mult: Optional[Callable[[T, T], T]] = None, add_id: Optional[T] = None):
    add = add or (lambda x, y: x + y)
    mult = mult or (lambda x, y: x * y)
    add_id = 0 if not add_id else add_id
    n, p, m = len(A), len(A[0]), len(B[0])
    C = [[cp(add_id) for _ in range(n)] for _ in range(m)]
    for i in range(n):
        for j in range(p):
            for k in range(m):
                C[i][k] = add(C[i][k], mult(A[i][j], B[j][k]))
    return C

# def pow_matrix
