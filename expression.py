from typing import Tuple, Union, List
from copy import deepcopy as cp


def gcd(a: int, b: int):
    while b:
        a, b = b, a % b
    return a


class Rational:
    __slots__ = ["p", "q"]

    def __init__(self, _p: int, _q: int):
        self.p, self.q = _p, _q
        self.simplify()

    def simplify(self):
        g = gcd(self.p, self.q)
        self.p, self.q = self.p // g, self.q // g

    def __add__(self, other):
        if isinstance(other, Rational):
            return cp(self).__iadd__(other)
        elif isinstance(other, (Polynomial, RationalFunc, RESum)):
            return other.__add__(self)
        raise NotImplementedError()

    def __iadd__(self, other: "Rational"):
        if not isinstance(other, Rational):
            raise NotImplementedError()
        self.p *= other.q
        self.p += other.p * self.q
        self.q *= other.q
        self.simplify()
        return self

    def __sub__(self, other):
        return cp(self).__isub__(other)

    def __isub__(self, other):
        return self.__iadd__(Rational(-other.p, other.q))

    def __mul__(self, other):
        if isinstance(other, Rational):
            return cp(self).__imul__(other)
        elif isinstance(other, (Polynomial, RationalFunc, RESum)):
            return other * self

    def __imul__(self, other):
        if not isinstance(other, Rational):
            raise NotImplementedError()
        self.p *= other.p
        self.q *= other.q
        self.simplify()
        return self

    def __floordiv__(self, other):
        return cp(self).__ifloordiv__(other)

    def __ifloordiv__(self, other):
        self.p *= other.q
        self.q *= other.p
        self.simplify()
        return self

    def __getitem__(self, item):
        return self.q if item else self.p

    def __setitem__(self, item, x):
        if item:
            self.q = x
        else:
            self.p = x


class Polynomial:
    __slots__ = ["a"]

    def __init__(self, _a: List[Rational]):
        self.a = _a

    def simplify(self):
        while len(self.a) > 1 and self.a[-1].p == 0:
            self.a.pop()

    def _shift(self, n):
        self.a = [cp(zero_rational) for _ in range(n)] + self.a

    def __add__(self, other):
        if isinstance(other, (Rational, Polynomial)):
            return cp(self).__iadd__(other)
        elif isinstance(other, (RationalFunc, RESum)):
            return other.__add__(self)
        raise NotImplementedError()

    def __iadd__(self, other):
        if isinstance(other, Rational):
            self[0] += other
        elif isinstance(other, Polynomial):
            while len(self.a) < len(other.a):
                self.a.append(cp(zero_rational))
            for self_coeff, other_coeff in zip(self, other):
                self_coeff += other_coeff
        self.simplify()
        return self

    def __sub__(self, other):
        return cp(self).__isub__(other)

    def __isub__(self, other):
        return self.__iadd__(other * Rational(-1, 1))

    def __mul__(self, other):
        if isinstance(other, (Rational, Polynomial)):
            return cp(self).__imul__(other)
        elif isinstance(other, (RationalFunc, RESum)):
            return other.__mul__(self)
        raise NotImplementedError()

    def __imul__(self, other):
        if isinstance(other, Rational):
            for coeff in self:
                coeff *= other
        elif isinstance(other, Polynomial):
            old_self = cp(self)
            self.a.clear()
            for i, coeff_f in enumerate(old_self):
                self.__iadd__((coeff_f * other).shift(i))
        return self

    def __divmod__(self, b):
        a = cp(self)
        q = cp(zero_poly)  # remainder
        while len(a) >= max(2, len(b)):
            temp = cp(b)  # holds multiple of b to subtract from a
            # replace leading coeff of b with leading coeff of a
            temp *= a[-1] // b[-1]
            # bump up degree
            temp *= Polynomial.monomial(len(a) - len(b))
            # add to quotient
            q += temp
            # subtract
            a -= temp
        return q, a

    def __floordiv__(self, other):
        if isinstance(other, Rational):
            return self.__mul__(Rational(other.q, other.p))
        elif isinstance(other, Polynomial):
            return self.__divmod__(other)[0]
        elif isinstance(other, (RationalFunc, RESum)):
            return other.__floordiv__(self)
        raise NotImplementedError()

    def __mod__(self, other):
        return self.__divmod__(other)[1]

    def __getitem__(self, item: int):
        return self.a[item]

    def __setitem__(self, item: int, x: Rational):
        self.a[item] = x

    def __iter__(self):
        return self.a

    def __len__(self):
        return len(self.a)

    @staticmethod
    def monomial(n: int) -> "Polynomial":
        return Polynomial([cp(zero_rational) for _ in range(n)] + [cp(one_rational)])


class RationalFunc:
    __slots__ = ["f", "g"]

    def __init__(self, _f: Polynomial, _g: Polynomial):
        self.f, self.g = _f, _g

    def simplify(self):
        self.f.simplify()
        self.g.simplify()

    def __add__(self, other):
        if isinstance(other, Rational):
            other = Polynomial([other])
        if isinstance(other, Polynomial):
            other = RationalFunc(cp(other), one_poly)
        if isinstance(other, RationalFunc):
            return RESum([cp(self), cp(other)])
        if isinstance(other, RESum):
            return other + self

    def __sub__(self, other):
        return cp(self) + (other * Rational(-1, 1))

    def __mul__(self, other):
        if isinstance(other, (Rational, Polynomial, RationalFunc)):
            return cp(self).__imul__(other)
        elif isinstance(other, RESum):
            return other.__mul__(self)
        raise NotImplementedError()

    def __imul__(self, other):
        if isinstance(other, (Rational, Polynomial)):
            self.f *= other
        elif isinstance(other, RationalFunc):
            self.f *= other.f
            self.g *= other.g
        return self


class RESum:
    __slots__ = ["a"]

    def __init__(self, _a: List[RationalFunc]):
        self.a = _a
        self.simplify()

    def simplify(self):
        for i in reversed(range(len(self.a))):
            for j in range(i):
                if self.a[i].g == self.a[j].g:
                    self.a[j].f += self.a[i].f
                    del self.a[i]
                    break

    def __add__(self, other: Union[Rational, Polynomial, RationalFunc, "RESum"]) -> "RESum":
        if isinstance(other, Rational):
            other = Polynomial([other])
        if isinstance(other, Polynomial):
            other = RationalFunc(other, cp(one_poly))
        if isinstance(other, RationalFunc):
            other = RESum([other])
        if isinstance(other, RESum):
            return RESum(self.a + other.a)
        raise NotImplementedError()

    def __sub__(self, other):
        return self + (other * Rational(-1, 1))

    def __mul__(self, other):
        if isinstance(other, (Rational, Polynomial, RationalFunc)):
            return RESum([rat_fun * other for rat_fun in self.a])
        if isinstance(other, RESum):
            return RESum([x * y for x in self for y in other])
        raise NotImplementedError()

    def __iter__(self):
        return self.a

    def __len__(self):
        return len(self.a)

    def __getitem__(self, item):
        return self.a[item]

    def __setitem__(self, key, value):
        self.a[key] = value

zero_rational = Rational(0, 1)
one_rational = Rational(1, 1)

zero_poly = Polynomial([cp(zero_rational)])
one_poly = Polynomial([cp(one_rational)])

zero_rat_func = RationalFunc(cp(zero_poly), cp(one_poly))
one_rat_func = RationalFunc(cp(one_poly), cp(one_poly))

zero_REsum = RESum([cp(zero_rat_func)])
one_REsum = RESum([cp(one_rat_func)])


# def fmt_rat_fun(f: RationalFunc) -> str:
#     return "/".join(f"[{fmt_polynomial(poly)}]" for poly in f) if f[1] != one_poly else fmt_polynomial(f[0])
#
#
# def fmt_REsum(f: RESum) -> str:
#     return " + ".join(f"{fmt_rat_fun(rat_fun)}" for rat_fun in f if rat_fun != zero_rat_func) or "0"
#
#
# def evaluate_poly_at_rat(f: Polynomial, x: Rational) -> Rational:
#     res = cp(zero_rational)
#     for coeff in reversed(f):
#         add_rational(res, coeff)
#         mult_rational(res, x)
#     return res
#
#
# def evaluate_rat_fun_at_rat(f: RationalFunc, x: Rational) -> Rational:
#     return divide_rational(evaluate_poly_at_rat(f[0], x), evaluate_poly_at_rat(f[1], x))
#
#
# def evaluate_REsum_at_rat(f: RESum, x: Rational) -> Rational:
#     res = cp(zero_rational)
#     for rat_fun in f:
#         add_rational(res, evaluate_rat_fun_at_rat(rat_fun, x))
#     return res
#
#
# def compare_rational(a: Rational, b: Rational) -> int:
#     return -1 if a[0] * b[1] < a[1] * b[0] else 0 if a[0] * b[1] == a[1] * b[0] else 1
