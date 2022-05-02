from expression import *


def check_poly_neg_geq_1(f: Polynomial) -> bool:
    if compare_rational(evaluate_poly_at_rat(f, one_rational), zero_rational) < 0:
        return False
    sturm = sturm_sequence(f)


def V(_sturm: List[Polynomial], x: Rational) -> int:
    sturm_eval = [evaluate_poly_at_rat(f, x) for f in _sturm]
    return sum(1 for i in range(len(sturm_eval)) if i and sturm_eval[i] != sturm_eval[i - 1])


def unique_zeros_in_region(sturm: List[Polynomial], a: Rational, b: Rational) -> int:
    return V(sturm, b) - V(sturm, a)


def sturm_sequence(f: Polynomial) -> List[Polynomial]:
    ret = [f, derivative(f)]
    while ret[-1] != zero_poly:
        ret.append(mult_poly_scalar(mod_poly(ret[-2], ret[-1])[0], [-1, 1]))
    return ret


def yun_factorization(f: Polynomial) -> List[Polynomial]:
    a = gcd_poly(f, derivative(f))
    b = mod_poly(f, a)[1]
    c = mod_poly(derivative(f), a)[1]
    d = add_poly(cp(c), mult_poly_scalar(derivative(b), [-1, 1]))
    res = []
    while 1:
        a = gcd_poly(b, d)
        res.append(a)
        b = mod_poly(b, a)[1]
        c = mod_poly(d, a)[1]
        d = add_poly(c, mult_poly_scalar(derivative(b), [-1, 1]))
        if b == one_poly:
            break
    return res


def derivative(f: Polynomial) -> Polynomial:
    return [mult_rational([i, 1], a_i) for i, a_i in enumerate(f) if i]




def gcd_poly(a: Polynomial, b: Polynomial) -> Polynomial:
    print(a, b)
    return a if b == zero_poly else gcd_poly(b, mod_poly(a, b)[0])
