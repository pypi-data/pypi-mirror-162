"""
Fraxtionz, by Elia Toselli.
A module to manage fractions with precision.
"""

import math
from debtcollector import removes


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

    def __neg__(self):
        return Fraction(0-self.n, self.d)

    def __sub__(self, other):
        if isinstance(other, int):
            other = Fraction(other)
        return self + other.__neg__()

    def __rsub__(self, other):
        if isinstance(other, int):
            other = Fraction(other)
        return other + self.__neg__()

    def floatdump(self):
        """ Returns the conventional floating-point value from the fraction """
        return float(self.n / self.d)

    @removes.remove
    def intdump(self):
        """ Returns the truncated int value from the fraction.
        See also: floatdump
        Deprecated since version 2.1.1rc3: it truncates instead of rounding.
        This method shouldn't used, because it removes precision from the number."""
        return int(self.floatdump())
