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



def play_with_funcs():
    my_rat_sum = re_sum.RESum([
        RationalFunc(
            Polynomial([1]), 
            Polynomial([0, 1])
            ),
        RationalFunc(
            Polynomial([0, 0, 1]),
            Polynomial([1, 1])
            ),
        RationalFunc(
            Polynomial([0, 1, 2, 3]),
            Polynomial([1, 1])
        ),
        RationalFunc(
            Polynomial([1, 2, 3, 5]),
            Polynomial([1])
        )
    ])

    my_rat_sum += RationalFunc(
        Polynomial([0, 2]),
        Polynomial([0, 1])
    )

    my_rat_sum += Polynomial([0, 0, 4])

    my_rat_sum += Rational(4, 24)

    zero_re = re_sum.zero_REsum
    print(zero_re)
    two_re = re_sum.one_REsum + re_sum.one_REsum
    print(two_re)
    two_re.simplify()
    print(two_re)

    print(my_rat_sum)
    my_rat_sum.simplify()
    print(my_rat_sum)





if __name__ == "__main__":
    main()
