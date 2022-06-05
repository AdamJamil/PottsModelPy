"""This module contains expression objects that represent numbers and symbolic expressions"""


from __future__ import annotations
from typing import Dict, Iterable, Optional, Union, List
from copy import deepcopy as cp

from polynomial import Polynomial, zero_poly
from rational import Rational, RAT_T, zero_rational
from rational_func import zero_rat_func, one_rat_func, RationalFunc, RF_T, _RF_T
import expr_utils


class RESum:
    """
    Sum of rational expressions, which are members of \\mathbb{Q}[x] but stored
    as individual rationals for lazy computation.
    """
    __slots__ = ["a"]

    def __init__(self, _a: Dict[Polynomial, Polynomial]) -> None:
        self.a = _a
        self.simplify()

    def sum_terms(self) -> RationalFunc:
        res = cp(zero_rat_func)
        for x in self:
            res += x
        return res

    def simplify(self) -> None:
        """Pairs up equal denominators"""
        for i in reversed(range(len(self.a))):
            self.a[i].simplify()
            if self.a[i].f == zero_poly:
                del self.a[i]
                break
            for j in range(i):
                if self.a[i].g == self.a[j].g:
                    self.a[j].f += self.a[i].f
                    del self.a[i]
                    break

    def __add__(self, other: RES_T) -> RESum:
        return cp(self).__iadd__(other)

    def __iadd__(self, other: RES_T) -> RESum:
        other = expr_utils.cast_up(other, RESum)
        self.a += other.a
        return self

    def __sub__(self, other: RES_T) -> RESum:
        return self + (other * Rational(-1, 1))

    def __mul__(self, other: RES_T) -> RESum:
        if isinstance(other, RF_T):
            return RESum([rat_fun * other for rat_fun in self.a])
        if isinstance(other, RESum):
            return RESum([self.sum_terms() * other.sum_terms()])
        raise NotImplementedError()

    def __call__(self, x: RAT_T) -> Optional[Rational]:
        res = cp(zero_rational)
        for rat_fun in self:
            y = rat_fun(x)
            if y is None:
                return None
            res += y
        return res

    def __iter__(self) -> Iterable[RationalFunc]:
        return iter(self.a)

    def __len__(self) -> int:
        return len(self.a)

    def __getitem__(self, item: int) -> RationalFunc:
        return self.a[item]

    def __setitem__(self, key: int, value: RationalFunc) -> None:
        self.a[key] = value

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return " + ".join(f"{str(rat_fun)}" for rat_fun in self if rat_fun != zero_rat_func) or "0"

    def __eq__(self, o: RESum) -> bool:
        o = expr_utils.cast_up(o, RESum, read_only=True)
        return isinstance(o, RESum) and self.sum_terms() == o.sum_terms()
        
    def __deepcopy__(self, memodict={}):
        res = EmptyRESum()
        res.a = [cp(x) for x in self.a]
        res.__class__ = RESum
        return res

class EmptyRESum(object):
    __slots__ = ["a"]

zero_REsum = RESum([cp(zero_rat_func)])
one_REsum = RESum([cp(one_rat_func)])


RES_T = Union[RF_T, RESum]
_RES_T = *_RF_T, RESum
