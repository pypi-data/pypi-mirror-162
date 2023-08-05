"""
Fraxtionz, by Elia Toselli.
A module to manage fractions with precision.
"""

import math


class Fraction(object):
    """
The main fraction class.
    """
    def __init__(self, n, d=1):
        """Creates a Fraction object.
        Arguments: n : numerator
                   d : denominator > 0"""
        assert isinstance(n, int)
        assert isinstance(d, int)
        if d == 0:
            raise ZeroDivisionError
        if d < 0:
            raise NotImplementedError("Can't handle denominators <0")
        div = math.gcd(n, d)
        self.n = n // div
        self.d = d // div

    def __str__(self):
        return "{}/{}".format(self.n, self.d)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def lcm(n, m):
        """ Calculates the lesser common multiple """
        return (n * m) / math.gcd(n, m)

    def lcden(self, other):
        """ Calculates the lesser common denominator """
        return Fraction.lcm(self.d, other.d)

    def __add__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.n * other.d + other.n * self.d,
                            self.d * other.d)
        elif isinstance(other, int):
            other = Fraction(other)
            return Fraction(self.n * other.d + other.n * self.d,
                            self.d * other.d)

    def __radd__(self, other):
        return self.__add__(other)

    def __eq__(self, other):
        return self.n == other.n and self.d == other.d

    def __lt__(self, other):
        return self.n * other.d < self.d * other.n

    def __le__(self, other):
        return self == other or self < other

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    def __mul__(self, other):
        return Fraction(self.n * other.n, self.d * other.d)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __invert__(self):
        return Fraction(self.d, self.n)

    def __truediv__(self, other):
        return self.__mul__(other.__invert__())

    def __floordiv__(self, other):
        result = self / other
        return result.n // result.d

    def __rtruediv__(self, other):
        if isinstance(other, int):
            other = Fraction(other)
        return other.__truediv__(self)

    def __rfloordiv__(self, other):
        if isinstance(other, int):
            other = Fraction(other)
        return other.__floordiv__(self)
