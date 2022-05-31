from copy import deepcopy as cp

from rational import zero_rational, one_rational, Rational
from polynomial import zero_poly, one_poly, Polynomial
from rational_func import zero_rat_func, one_rat_func, RationalFunc
from re_sum import zero_REsum, one_REsum, RESum


class TestExpression:
    def __init__(self):
        for attr in dir(self):
            if attr[:4] == "test":
                self.__getattribute__(attr)()
        self.test_default_values()
        print("all test OK")

    def test_default_values(self):
        assert zero_rational == Rational(0, 1)
        assert one_rational == Rational(1, 1)

        assert zero_poly == Polynomial([0])
        assert one_poly == Polynomial([1])

        assert zero_rat_func == RationalFunc(cp(zero_poly), cp(one_poly))
        assert one_rat_func == RationalFunc(cp(one_poly), cp(one_poly))

        assert zero_REsum == RESum([zero_rat_func])
        assert one_REsum == RESum([one_rat_func])

    def test_monomial(self):
        assert Polynomial.monomial(0) == one_poly
        assert Polynomial.monomial(0) * 3 == Polynomial([3])

        assert Polynomial.monomial(1) == Polynomial([cp(zero_rational), cp(one_rational)])
        assert (
            Polynomial.monomial(3)
            == Polynomial([0, 0, 0, 1])
        )

    def test_rational(self):
        x, y = Rational(3, 3), Rational(9, 4)
        x.simplify()
        y.simplify()
        assert (x.p, x.q) == (1, 1)
        assert (y.p, y.q) == (9, 4)

        assert one_rational + one_rational == Rational(2, 1)
        assert one_rational + zero_rational == one_rational
        assert Rational(3, 2) + Rational(7, 3) == Rational(23, 6)
        assert Rational(1, 3) + Rational(1, 3) == Rational(2, 3)

        assert Rational(3, 1) * Rational(4, 2) == Rational(6, 1)
        assert zero_rational * Rational(-34, 39495) == zero_rational

    def test_polynomial(self):
        assert one_poly * 3 == Polynomial([Rational(3, 1)])
        assert (
            (Polynomial.monomial(2) + Polynomial.monomial(4)) * Rational(7, 2)
            == Polynomial([0, 0, Rational(7, 2), 0, Rational(7, 2)])
        )

        assert Polynomial.monomial(2) + Polynomial.monomial(1) == Polynomial([0, 1, 1])
        assert (
            Polynomial.monomial(2) + (Polynomial.monomial(3) * 3) + Polynomial.monomial(2) 
            == Polynomial([0, 0, 2, 3])
        )

        assert Polynomial.monomial(3) * Polynomial.monomial(4) == Polynomial.monomial(7)
        assert (
            (Polynomial.monomial(1) * Rational(3, 2))
            * (Polynomial.monomial(2) + Polynomial.monomial(3))
            == Polynomial([0, 0, 0, Rational(3, 2), Rational(3, 2)])
        )

        assert Polynomial([1] * 3) * Polynomial([1] * 3) == Polynomial([1, 2, 3, 2, 1])
        assert (
            Polynomial([Rational(3, 2) for _ in range(4)])
                * Polynomial([Rational(3, 2) for _ in range(4)])
            == Polynomial([
                Rational(9, 4),
                Rational(9, 2),
                Rational(27, 4),
                9,
                Rational(27, 4),
                Rational(9, 2), Rational(9, 4)
            ])
        )

        f = Polynomial.monomial(1)
        f *= f
        assert f == Polynomial([0, 0, 1])

    def test_yun(self):
        a_1 = Polynomial([-2, 1])
        a_2 = Polynomial([-1, 1])
        a_5 = Polynomial([1, 0, 1])
        f = a_1 * a_2 * a_2 * a_5 * a_5 * a_5 * a_5 * a_5
        assert f.yun_factorization() == [a_1, a_2, one_poly, one_poly, a_5]

    