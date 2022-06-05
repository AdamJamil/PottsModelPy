from random import random
from typing import List
from matrix_utils import *
from re_sum import *
import time


def is_partial_ordering(r: List[List[int]]) -> bool:
    n = len(r)
    reflexive = all(r[i][i] for i in range(n))
    antisymmetric = all(r[i][j] != r[j][i] for i in range(n) for j in range(n) if i != j)
    transitive = all(not (r[i][j] and r[j][k]) or r[i][k] for i in range(n) for j in range(n) for k in range(n))
    return reflexive and antisymmetric and transitive


def get_max_partial_ordering(n: int) -> List[List[int]]:
    '''
    Implement algo 4.11 - Find Maximal Partial Ordering

    param n is the size of the graph (for K_n, the complete graph)
    '''
    A = generate_transition_matrix(n)
    s = len(A)
    r = [[True] * s for _ in range(s)] # Why is the datatype wrong ???
    A_expo = cp(A)
    for _ in range(3):
        # print(A_expo)
        for i in range(s):
            for j in range(s):
                if r[j][i] and (A_expo[i][0] - A_expo[j][0]).sum_terms().f.pos_above_1():
                    r[j][i] = False
        print("start mult")
        start = time.perf_counter_ns()
        A_expo = mult_matrix(A_expo, A, add_id=zero_REsum)
        print((time.perf_counter_ns() - start) / 1000000000)
    print("\n".join(map(str, r)))
    # assert is_partial_ordering(r)
    return r
