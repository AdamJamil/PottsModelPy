'''
Expression Representations:
 - Rational, member of \\mathbb{Q}
    * defined with params p, q for p/q
    * simplified via gcd
 - Polynomial, member of \\mathbb{Q}[x]
    * defined with list of rationals
        [0, 2, 0, 3] -> 0 + 2x + 0 + 3x^2
    * simplified by simplifying coeffs and cutting off zero terms
        [0, 2/4, 0, 0] -> [0, 1/2]
 - RationalFunc, two polynomials stacked above each other
    * defined with two polynomials, f, g for f/g
    * simplified by simplifying polynomials and checking if 0 poly
 - RESum, sum of rational expressions
    * defined with list of RationalFuncs
    * simplfied by combining terms with same denom

Utils:
  - cast_up
    * given an int, rational, polynomial, rationalfunc, or resum
      it will cast up to the specified type

Integers are automatically cast up/down into the necessary types.
To construct 1/x + x^2/(2x + 1), you could for example do:

dummyThiccSum = RESum([ 
    RationalFunct(
        1,
        Polynomial([0, 1])
    ),
    RationalFunc(
        Polynomial([0, 1]) * Polynomial([0, 1]),
        Polynomial([0, 2]) + 1
    )
])
'''

from __future__ import annotations
from functools import total_ordering
from typing import Any, List, Tuple, Iterable, Union, Optional, Type
from copy import deepcopy as cp
import json
import time











types = "int", "Rational", "Polynomial", "RationalFunc", "RESum"

def cast_up(x: Any, target_type: Type, read_only: bool=False) -> Any:
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





















class Polynomial:
    """Elements of \\mathbb{Q}[x], where coefficients are represented as a list [a_0, ..., a_n]"""
    __slots__ = ["a", "_sturm"]

    def __init__(self, _a: List[RAT_T]) -> None:
        if not isinstance(_a, list) or any(not isinstance(x, _RAT_T) for x in _a):
            raise TypeError("ur input to polynomial sucks")
        self.a = [Rational(x, 1) if isinstance(x, int) else x for x in _a]
        self._sturm = None

    def simplify(self) -> None:
        """Clear zero coefficients off back"""
        for coeff in self:
            coeff.simplify()
        while len(self.a) > 1 and self.a[-1].p == 0:
            self.a.pop()

    def _shift(self, n: int) -> Polynomial:
        """Multiply by x^n"""
        self.a = [cp(zero_rational) for _ in range(n)] + self.a
        return self

    def _get_monic(self) -> Polynomial:
        return cp(self) * Rational(self[-1].q, self[-1].p)

    def __add__(self, other: POLY_T) -> Polynomial:
        return cp(self).__iadd__(other)

    def __iadd__(self, other: POLY_T) -> Polynomial:
        if isinstance(other, _RAT_T):
            self[0] += other
        elif isinstance(other, Polynomial):
            while len(self.a) < len(other.a):
                self.a.append(cp(zero_rational))
            for self_coeff, other_coeff in zip(self, other):
                self_coeff += other_coeff
        else:
            raise NotImplementedError()
        self.simplify()
        return self

    def __sub__(self, other: POLY_T) -> Polynomial:
        return cp(self).__isub__(other)

    def __isub__(self, other: POLY_T) -> Polynomial:
        return self.__iadd__(other * Rational(-1, 1))

    def __mul__(self, other: POLY_T) -> Polynomial:
        return cp(self).__imul__(other)

    def __imul__(self, other: POLY_T) -> Polynomial:
        if isinstance(other, _RAT_T):
            for coeff in self:
                coeff *= other
        elif isinstance(other, Polynomial):
            if other is self:
                other = cp(self)
            old_self = cp(self)
            self.a.clear()
            res = []
            for new_deg in range(len(old_self) + len(other) - 1):
                res.append(cp(zero_rational))
                for pos_1, self_coeff in enumerate(old_self):
                    if new_deg - pos_1 < 0:
                        break
                    if new_deg - pos_1 < len(other):
                        res[-1] += self_coeff * other[new_deg - pos_1]
            self.a = res
        else:
            raise NotImplementedError()
        return self

    def __divmod__(self, b: Polynomial) -> Tuple[Polynomial, Polynomial]:
        a = cp(self)
        q = Polynomial([0])  # remainder
        while len(a) >= len(b):
            if len(a) == len(b) == 1 and a[0].p == 0:
                break
            temp = cp(one_poly)  # record multiple of b to subtract from a
            temp *= a[-1] // b[-1]  # replace leading coeff of b with leading coeff of a
            temp._shift(len(a) - len(b))  # bump up degree
            q += temp  # add to quotient
            a -= temp * b  # subtract
        return q, a

    def __floordiv__(self, other: POLY_T) -> Polynomial:
        other = cast_up(other, Polynomial, read_only=True)
        return self.__divmod__(other)[0]

    def __mod__(self, other: Polynomial) -> Polynomial:
        return self.__divmod__(other)[1]

    def __call__(self, x: RAT_T) -> Rational:
        res = cp(zero_rational)
        for coeff in reversed(self):
            res += coeff
            res *= x
        return res

    def __getitem__(self, item: int) -> Rational:
        return self.a[item]

    def __setitem__(self, item: int, x: Rational) -> None:
        self.a[item] = x

    def __iter__(self) -> Iterable[Rational]:
        return iter(self.a)

    def __len__(self) -> int:
        return len(self.a)

    @staticmethod
    def monomial(n: int) -> Polynomial:
        """Returns x^n"""
        return Polynomial([cp(zero_rational) for _ in range(n)] + [cp(one_rational)])

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def _fmt_monomial(deg: int, coeff: Rational) -> str:
        super_script = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        expo = "" if deg <= 1 else "".join(super_script[ord(c) - ord("0")] for c in str(deg))
        coeff_str = str(coeff.p) if coeff.q == 1 else f"({coeff.p}/{coeff.q})"
        var_str = "" if not deg else f"λ{expo}"
        return (coeff_str + var_str if coeff_str != "1" else var_str if var_str else "1") or "0"

    def __str__(self) -> str:
        ret = "+".join(Polynomial._fmt_monomial(i, a) for i, a in enumerate(self) if a[0])
        return ret.replace("+-", "-").replace("-1λ", "-λ") or "0"

    def __eq__(self, o: Polynomial) -> bool:
        o = cast_up(o, Polynomial, read_only=True)
        return isinstance(o, Polynomial) and (self - o).a == [zero_rational]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,  sort_keys=True, indent=4)

    def pos_above_1(self) -> bool:
        if self == zero_poly:
            return True
        return self(1) >= 0 and all(f.sq_fr_pos_above_1() for f in self.yun_factorization())

    def sq_fr_pos_above_1(self) -> bool:
        # main idea: find all ranges with only one root inside, and check f(end pts) >= 0
        f = cp(self)
        while f(1) == 0:
            f //= Polynomial([-1, 1])  # keep dividing out x - 1
        if f(1) < 0:
            return False

        root_lb, root_ub = Rational(1, 1), f.root_upper_bound()
        stack = [(root_lb, root_ub)]
        single_root_ints = []
        while stack:
            a, b = stack.pop()
            roots = f.unique_zeros_in_region(a, b)
            if roots == 1:
                single_root_ints.append((a, b))
            elif roots > 1:
                stack.append((a, (a + b) // 2))
                stack.append(((a + b) // 2, b))
        assert len(single_root_ints) == f.unique_zeros_in_region(root_lb, root_ub)

        for a, b in single_root_ints:
            if f(b) == 0:  # edge case
                # we want our root to be in (a, b)
                # we try to extend our interval by some r = 2^-i, making sure to disinclude any higher root
                r = cp(one_rational)
                while f.unique_zeros_in_region(b,  b + r):
                    r //= 2
                b += r
            if f(a) < 0 or f(b) < 0:
                return False
        return True

    def yun_factorization(self) -> List[Polynomial]:
        if self == zero_poly:
            raise TypeError("fuck you")
        a = self.gcd(self.derivative())
        b = self // a
        c = self.derivative() // a
        d = c - b.derivative()
        res = []
        while 1:
            a = b.gcd(d)
            res.append(a)
            b //= a
            c = d // a
            d = c - b.derivative()
            if len(b) == 1:
                res[-1] *= b
                break
        return res

    def gcd(self, b: Polynomial) -> Polynomial:
        """Euclidean algorithm on polynomials"""
        a = self
        while b != zero_poly:
            a, b = b, a % b
        return a._get_monic()

    def V(self, x: Rational) -> int:
        """V function as defined by Sturm's theorem"""
        sturm_eval = [y for f in self.sturm if (y := f(x)) != 0]
        return sum(
            1 for i in range(len(sturm_eval)) 
            if i and (sturm_eval[i] > 0) != (sturm_eval[i - 1] > 0)
        )

    def unique_zeros_in_region(self, a: Rational, b: Rational) -> int:
        return self.V(a) - self.V(b)

    @property
    def sturm(self) -> List[Polynomial]:
        if self._sturm:
            return self._sturm
        ret = [cp(self), self.derivative()]
        while ret[-1] != zero_poly:
            ret.append((ret[-2] % ret[-1]) * -1)
        return ret

    def derivative(self) -> Polynomial:
        res = cp(zero_poly)
        for i, coeff in enumerate(self):
            if i:
                res += Polynomial.monomial(i - 1) * coeff * i
        return res

    def root_upper_bound(self) -> Rational:
        mx = 0
        for i in range(len(self) - 1):
            res = self[i] // self[-1]
            if res.p < 0:
                res.p = -res.p
            mx = max(mx, res)
        return mx + 1

    def __deepcopy__(self, memodict={}):
        res = EmptyPoly()
        res.a = [cp(x) for x in self.a]
        res._sturm = None
        res.__class__ = Polynomial
        return res


class EmptyPoly(object):
    __slots__ = ["a", "_sturm"]

zero_poly = Polynomial([0])
one_poly = Polynomial([1])

POLY_T = Union[Polynomial, RAT_T]
_POLY_T = Polynomial, *_RAT_T
















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
        other = cast_up(other, RationalFunc, read_only=True)
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














class RESum:
    """
    Sum of rational expressions, which are members of \\mathbb{Q}[x] but stored
    as individual rationals for lazy computation.
    """
    __slots__ = ["a"]

    def __init__(self, _a: List[RationalFunc]) -> None:
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
        other = cast_up(other, RESum)
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
        o = cast_up(o, RESum, read_only=True)
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




















