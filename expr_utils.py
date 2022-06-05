from typing import Any, Type
from copy import deepcopy as cp
import time

types = "int", "Rational", "Polynomial", "RationalFunc", "RESum"

tot_time = 0
import_time = 0
cast_time = 0

def cast_up(x: Any, target_type: Type, read_only: bool=False) -> Any:
    global import_time, cast_time

    start_time = time.perf_counter_ns()
    from rational import Rational
    from polynomial import Polynomial, one_poly
    from rational_func import RationalFunc
    from re_sum import RESum
    import_time += time.perf_counter_ns() - start_time

    start_time = time.perf_counter_ns()
    if not read_only:
        x = cp(x)

    ptr = 0
    this_type = type(x).__name__
    target_type = target_type.__name__
    # print(this_type)
    while ptr < 5 and this_type != types[ptr]:
        ptr += 1
    if ptr == 5:
        raise TypeError(f"input to cast_up is of invalid type {this_type}")

    while ptr < 5:
        curr_type = types[ptr]
        if type(x).__name__ != curr_type:
            raise TypeError(f"{type(x)} does not match {curr_type}")
        if target_type == curr_type:
            cast_time = time.perf_counter_ns() - start_time
            return x
        if curr_type == "int":
            x = Rational(x, 1)
        elif curr_type == "Rational":
            x = Polynomial([x])
        elif curr_type == "Polynomial":
            x = RationalFunc(x, cp(one_poly))
        elif isinstance(x, RationalFunc):
            x = RESum([x])
        elif target_type == RESum:
            raise TypeError(f"target type {target_type} is invalid")
        ptr += 1

    raise TypeError("what the cast_up doin")

def print_timing_breakdown():
    div_factor = 1_000_000_000
    tot_time = import_time + cast_time

    print("Total Time: %.5f" % (tot_time / div_factor))
    print(" > import: %.5f | %.5f %%" %( import_time / div_factor, import_time / tot_time))
    print(" > cast:   %.5f | %.5f %%" %( cast_time / div_factor, cast_time / tot_time))


