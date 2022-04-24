from random import random
from typing import List
from matrix_utils import *
from expression import *


def is_partial_ordering(r: List[List[int]]) -> bool:
    n = len(r)
    reflexive = all(r[i][i] for i in range(n))
    antisymmetric = all(r[i][j] != r[j][i] for i in range(n) for j in range(n) if i != j)
    transitive = all(not (r[i][j] and r[j][k]) or r[i][k] for i in range(n) for j in range(n) for k in range(n))
    return reflexive and antisymmetric and transitive


def get_max_partial_ordering(n: int) -> List[List[int]]:
    A = generate_transition_matrix(n)
    s = len(A)
    r = [[True] * s for _ in range(s)]
    lambd, alpha = 1, 1.05
    while lambd <= 10:
        print(lambd)
        lambd *= alpha
        A_eval = evaluate_matrix_at_rational(A, [int(lambd * 100000), 100000])
        A_expo = cp(A_eval)
        for _ in range(20):
            for x in range(s):
                for y in range(s):
                    if compare_rational(A_expo[x][0], A_expo[y][0]) < 0:
                        r[x][y] = False
            A_expo = mult_matrix(A_expo, A_eval, add=add_rational, mult=mult_rational, add_id=zero_rational)
    print("\n".join(map(str, r)))
    assert is_partial_ordering(r)
    return r
