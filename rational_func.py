from __future__ import annotations
from typing import Iterable, Optional, Union
from copy import deepcopy as cp
import expr_utils

from polynomial import POLY_T, _POLY_T, one_poly, zero_poly, Polynomial
from rational import Rational, RAT_T

class RationalFunc:
    """Represents f/g, where f, g \\in \\mathbb{Q}[x]"""
    __slots__ = ["f", "g"]

    def __init__(self, _f: Polynomial, _g: Polynomial) -> None:
        self.f, self.g = _f, _g

    def simplify(self) -> None:
        """Simplify both f and g"""
        self.f.simplify()
        if self.f == zero_poly:
            self.g = cp(one_poly)
        else:
            self.g.simplify()

    def __add__(self, other: RF_T) -> RationalFunc:
        other = expr_utils.cast_up(other, RationalFunc, read_only=True)
        res = cp(self)
        res.f *= other.g
        res.f += other.f * res.g
        res.g *= other.g
        return res

    def __sub__(self, other: RF_T) -> RationalFunc:
        return self + (other * -1)

    def __mul__(self, other: RF_T) -> RationalFunc:
        return cp(self).__imul__(other)

    def __imul__(self, other: RF_T) -> RationalFunc:
        if isinstance(other, _POLY_T):
            self.f *= other
        elif isinstance(other, RationalFunc):
            self.f *= other.f
            self.g *= other.g
        else:
            raise NotImplementedError()
        return self

    def __call__(self, x: RAT_T) -> Optional[Rational]:
        num, denom = self.f(x), self.g(x)
        if denom.p == 0:
            return None
        return num // denom

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterable[Polynomial]:
        return iter((self.f, self.g))

    def __str__(self) -> str:
        return "/".join(f"[{str(poly)}]" for poly in self) if self.g != one_poly else str(self.f)

    def __eq__(self, o: RationalFunc) -> bool:
        if isinstance(o, int):
            o = Rational(o, 1)
        if isinstance(o, Rational):
            o = Polynomial([o])
        if isinstance(o, Polynomial):
            o = RationalFunc(o, cp(one_poly))
        return isinstance(o, RationalFunc) and self.f * o.g == self.g * o.f

    def __deepcopy__(self, memodict={}):
        return RationalFunc(cp(self.f), cp(self.g))

RF_T = Union[RationalFunc, POLY_T]
_RF_T = RationalFunc, *_POLY_T

zero_rat_func = RationalFunc(cp(zero_poly), cp(one_poly))
one_rat_func = RationalFunc(cp(one_poly), cp(one_poly))