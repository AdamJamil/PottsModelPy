from __future__ import annotations
import json
from typing import List, Tuple, Iterable, Union
from copy import deepcopy as cp
import expr_utils

from rational import Rational, _RAT_T, RAT_T, zero_rational, one_rational


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
        other = expr_utils.cast_up(other, Polynomial, read_only=True)
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
        o = expr_utils.cast_up(o, Polynomial, read_only=True)
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
