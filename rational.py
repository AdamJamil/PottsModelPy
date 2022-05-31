from __future__ import annotations
from functools import total_ordering
from typing import Union
from copy import deepcopy as cp
from expr_utils import cast_up

def gcd(a: int, b: int):
    """Euclidean Algorithm"""
    while b:
        a, b = b, a % b
    return a

@total_ordering
class Rational:
    """Elements of \\mathbb{Q}"""
    __slots__ = ["p", "q"]

    def __init__(self, _p: int, _q: int) -> None:
        self.p, self.q = _p, _q

    def simplify(self) -> None:
        """Run gcd on args"""
        g = gcd(self.p, self.q)
        self.p, self.q = self.p // g, self.q // g

    def __add__(self, other: RAT_T) -> Rational:
        return cp(self).__iadd__(other)

    def __iadd__(self, other: RAT_T) -> Rational:
        other = cast_up(other, Rational, read_only=True)
        self.p = self.p * other.q + other.p * self.q
        self.q *= other.q
        self.simplify()
        return self

    def __sub__(self, other: RAT_T) -> Rational:
        return cp(self).__isub__(other)

    def __isub__(self, other: RAT_T) -> Rational:
        return self.__iadd__(other * -1)

    def __mul__(self, other: RAT_T) -> Rational:
        return cp(self).__imul__(other)

    def __imul__(self, other: RAT_T) -> Rational:
        if not isinstance(other, _RAT_T):
            raise NotImplementedError()
        if isinstance(other, int):
            other = Rational(other, 1)
        self.p *= other.p
        self.q *= other.q
        self.simplify()
        return self

    def __floordiv__(self, other: RAT_T) -> Rational:
        return cp(self).__ifloordiv__(other)

    def __ifloordiv__(self, other: RAT_T) -> Rational:
        if not isinstance(other, _RAT_T):
            raise NotImplementedError()
        if isinstance(other, int):
            other = Rational(other, 1)
        self.p *= other.q
        self.q *= other.p
        self.simplify()
        return self

    def __getitem__(self, item: int) -> int:
        return self.q if item else self.p

    def __setitem__(self, item: int, x: int):
        if item:
            self.q = x
        else:
            self.p = x

    def __eq__(self, o: RAT_T) -> bool:
        if isinstance(o, int):
            o = Rational(o, 1)
        return isinstance(o, Rational) and self.p * o.q == self.q * o.p

    def __lt__(self, o: RAT_T) -> bool:
        o = cast_up(o, Rational, read_only=True)
        return isinstance(o, Rational) and self.p * o.q < self.q * o.p

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.p) if self.q == 1 else f"{self.p}/{self.q}"

    def __deepcopy__(self, memodict={}):
        return Rational(self.p, self.q)

zero_rational = Rational(0, 1)
one_rational = Rational(1, 1)

RAT_T = Union[Rational, int]
_RAT_T = Rational, int
