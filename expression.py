from typing import Tuple, Union, List
from copy import deepcopy as cp

Rational = List[int]
Polynomial = List[Rational]
RationalFunc = Tuple[Polynomial, Polynomial]
RESum = List[RationalFunc]

zero_rational = [0, 1]
one_rational = [1, 1]

zero_poly = [cp(zero_rational)]
one_poly = [cp(one_rational)]

zero_rat_func = [cp(zero_poly), cp(one_poly)]
one_rat_func = [cp(one_poly), cp(one_poly)]

zero_REsum = [cp(zero_rat_func)]
one_REsum = [cp(one_rat_func)]


def monomial(n: int) -> Polynomial:
    return [cp(zero_rational) for _ in range(n)] + [cp(one_rational)]


def add_REsum(f: RESum, g: RESum) -> RESum:
    for num_g, denom_g in g:
        for num_f, denom_f in f:
            if denom_f == denom_g:
                add_poly(num_f, num_g)
                break
        else:
            f.append((cp(num_g), cp(denom_g)))
    return f


def gcd(a: int, b: int):
    return gcd(b, a % b) if b else a


def simplify_rational(a: Rational) -> Rational:
    g = gcd(*a)
    a[0] //= g
    a[1] //= g
    return a


def mult_rational(a: Rational, b: Rational) -> Rational:
    a[0] *= b[0]
    a[1] *= b[1]
    return simplify_rational(a)


def add_rational(a: Rational, b: Rational) -> Rational:
    a[0] *= b[1]
    a[1] *= b[1]
    a[0] += b[0] * (a[1] // b[1])
    return simplify_rational(a)


def mult_poly_scalar(f: Polynomial, a: Rational):
    for i in range(len(f)):
        mult_rational(f[i], a)
    return f


def mult_poly(f: Polynomial, g: Polynomial):
    _f = cp(f)
    f.clear()
    for i, coeff_f in enumerate(_f):
        temp = cp(g)
        mult_poly_scalar(temp, coeff_f)
        add_poly(f, [zero_rational for _ in range(i)] + temp)
    return f


def add_poly(f: Polynomial, g: Polynomial):
    while len(f) < len(g):
        f.append(cp(zero_rational))
    for i, coeff_g in enumerate(g):
        add_rational(f[i], coeff_g)
    return f


def fmt_monomial(deg: int, coeff: Rational) -> str:
    super = "⁰¹²³⁴⁵⁶⁷⁸⁹"
    expo = "" if deg <= 1 else "".join(super[ord(c) - ord("0")] for c in str(deg))
    p, q = coeff
    coeff_str = str(p) if q == 1 else f"({p}/{q})"
    var_str = ("" if not deg else f"λ{expo}")
    return coeff_str + var_str


def fmt_polynomial(f: Polynomial) -> str:
    ret = "+".join(fmt_monomial(i, a) for i, a in enumerate(f) if a[0] != 0)
    return ret or "0"


def fmt_rat_fun(f: RationalFunc) -> str:
    return "/".join(f"[{fmt_polynomial(poly)}]" for poly in f) if f[1] != one_poly else fmt_polynomial(f[0])


def fmt_REsum(f: RESum) -> str:
    return " + ".join(f"{fmt_rat_fun(rat_fun)}" for rat_fun in f if rat_fun != zero_rat_func) or "0"
