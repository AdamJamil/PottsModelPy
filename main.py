# import random
# from typing import Tuple, List
# from copy import deepcopy as cp

# from expression import *
from matrix_utils import generate_transition_matrix
from states import get_states
from polynomial import Polynomial
from re_sum import zero_REsum
from test import TestExpression
from partial_ordering import get_max_partial_ordering
# from functools import reduce
# from poly_utils import *
from rational import *

def main():
    # TestExpression()
    # print(get_states(3))
    # for row in generate_transition_matrix(3):
    #     print(" | ".join(str(f) for f in row))
    # for row in generate_transition_matrix(3):
    #     res = cp(zero_REsum)
    #     for x in row:
    #         res += x
    #     print(str(res))
    import cProfile
    pr = cProfile.Profile()
    pr.enable()
    get_max_partial_ordering(4)
    pr.disable()
    filename = 'profile.prof'  # You can change this if needed
    pr.dump_stats(filename)
    # print("\n".join(map(str, get_max_partial_ordering(6))))

    TestExpression()

if __name__ == "__main__":
    main()
