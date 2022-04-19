from expression import *


class TestExpression:
    def __init__(self):
        for attr in dir(self):
            if attr[:4] == "test":
                self.__getattribute__(attr)()
        self.test_default_values()

    def test_default_values(self):
        assert zero_rational == [0, 1]
        assert one_rational == [1, 1]

        assert zero_poly == [[0, 1]]
        assert one_poly == [[1, 1]]

        assert zero_rat_func == [[[0, 1]], [[1, 1]]]
        assert one_rat_func == [[[1, 1]], [[1, 1]]]

        assert zero_REsum == [[[[0, 1]], [[1, 1]]]]
        assert one_REsum == [[[[1, 1]], [[1, 1]]]]

    def test_monomial(self):
        assert monomial(0) == one_poly
        assert mult_poly_scalar(monomial(0), [3, 1]) == [[3, 1]]

        assert monomial(1) == [zero_rational, one_rational]
        assert monomial(3) == [zero_rational, zero_rational, zero_rational, one_rational]

    def test_rational(self):
        assert simplify_rational([3, 3]) == [1, 1]
        assert simplify_rational([9, 4]) == [9, 4]

        assert add_rational(cp(one_rational), one_rational) == [2, 1]
        assert add_rational(cp(one_rational), zero_rational) == one_rational
        assert add_rational([3, 2], [7, 3]) == [23, 6]
        assert add_rational([1, 3], [1, 3]) == [2, 3]

        assert mult_rational([3, 1], [4, 2]) == [6, 1]
        assert mult_rational(cp(zero_rational), [97, 3]) == zero_rational

    def test_polynomial(self):
        assert mult_poly_scalar(cp(one_poly), [3, 1]) == [[3, 1]]
        assert (
            mult_poly_scalar(add_poly(monomial(2), monomial(4)), [7, 2]) ==
            [zero_rational, zero_rational, [7, 2], zero_rational, [7, 2]]
        )

        assert add_poly(monomial(2), monomial(1)) == [zero_rational, one_rational, one_rational]
        assert (
            add_poly(add_poly(monomial(2), mult_poly_scalar(monomial(3), [3, 1])), monomial(2)) ==
            [zero_rational, zero_rational, [2, 1], [3, 1]]
        )

        assert mult_poly(monomial(3), monomial(4)) == monomial(7)
        assert (
            mult_poly(mult_poly_scalar(monomial(1), [3, 2]), add_poly(monomial(2), monomial(3))) ==
            [zero_rational, zero_rational, zero_rational, [3, 2], [3, 2]]
        )