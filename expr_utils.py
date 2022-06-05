from typing import Any, Type
from copy import deepcopy as cp


types = "int", "Rational", "Polynomial", "RationalFunc", "RESum"

def cast_up(x: Any, target_type: Type, read_only: bool=False) -> Any:
    from rational import Rational
    from polynomial import Polynomial, one_poly
    from rational_func import RationalFunc
    from re_sum import RESum

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
