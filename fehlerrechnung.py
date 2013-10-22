#!/usr/bin/env python3
# -*- coding: utf8 -*-

from decimal import Decimal, ROUND_DOWN, ROUND_UP
from numbers import Number


class BaseTerm:
    def __repr__(self):
        return self.display(2)

    def display(self, error_digits=1):
        if self.error == 0:
            return str(self.value)

        error = self.error
        value = self.value
        exponent = 0
        divisor = Decimal('10')
        while error >= 1:
            error /= divisor
            value /= divisor
            exponent += 1

        quantifier = Decimal(1)
        while error.quantize(quantifier, rounding=ROUND_DOWN) == 0:
            quantifier /= 10

        while error_digits > 1:
            quantifier /= 10
            error_digits -= 1

        if exponent == 0:
            return '({}±{})'.format(
                str(value.quantize(quantifier)),
                str(error.quantize(quantifier, rounding=ROUND_UP)))
        else:
            return '(({}±{})×10^{})'.format(
                str(value.quantize(quantifier)),
                str(error.quantize(quantifier, rounding=ROUND_UP)),
                exponent)

    @property
    def value(self):
        return self._value

    @property
    def error(self):
        return self._error

    @property
    def relerror(self):
        return abs(self.error / self.value)

    def __add__(self, other):
        return Sum(self, other)

    def __radd__(self, other):
        return Sum(other, self)

    def __sub__(self, other):
        return Difference(self, other)

    def __rsub__(self, other):
        return Difference(other, self)

    def __mul__(self, other):
        return Product(self, other)

    def __rmul__(self, other):
        return Product(other, self)

    def __truediv__(self, other):
        return Quotient(self, other)

    def __rtruediv__(self, other):
        return Quotient(other, self)

    __div__ = __truediv__

    def __pow__(self, other):
        return Power(self, other)

    def __rpow__(other, self):
        return Power(self, other)

    def __lt__(self, other):
        if isinstance(other, Number):
            return self.value + self.error < other
        elif isinstance(other, BaseTerm):
            return self.value + self.error < other.value - other.error
        else:
            raise NotImplemented()

    def __le__(self, other):
        return self == other or self < other

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.value - self.error <= other <= self.value + self.error
        elif isinstance(other, BaseTerm):
            return \
                self == other.value - other.error or \
                self == other.value + other.error
        else:
            raise NotImplemented()

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        if isinstance(other, Number):
            return self.value - self.error > other
        elif isinstance(other, BaseTerm):
            return self.value - self.error > other.value + other.error
        else:
            raise NotImplemented()

    def __ge__(self, other):
        return self == other or self > other


class Value(BaseTerm):
    def __init__(self, value, error=None, relerror=None):
        self._value = Decimal(str(value))
        if error is None and relerror is None:
            self._error = Decimal()
        elif error is not None:
            self._error = abs(Decimal(str(error)))
        else:
            self._error = abs(Decimal(str(relerror)) * self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = Decimal(str(value))

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        self._error = abs(Decimal(str(value)))

    @property
    def relerror(self):
        return abs(self.error / self.value)

    @relerror.setter
    def relerror(self, value):
        self._error = abs(Decimal(str(value)) * self.value)


class ErrorTerm(BaseTerm):
    def __init__(self, first, second):
        if not isinstance(first, BaseTerm):
            first = Value(first)
        if not isinstance(second, BaseTerm):
            second = Value(second)

        self._first = first
        self._second = second

    def display(self, error_digits=1):
        first = self._first.display(error_digits).splitlines()
        second = self._second.display(error_digits).splitlines()
        sel = super().display(error_digits)
        res = []
        while len(first) > 1 or len(second) > 1:
            res.append('({}{}{})'.format(
                first[0],
                self.__class__.symbol,
                second[0]))
            if len(first) > 1:
                first = first[1:]
            if len(second) > 1:
                second = second[1:]
        res.append('({}{}{})'.format(
            first[0],
            self.__class__.symbol,
            second[0]))
        res.append(sel)
        return '\n'.join(res)


class AbsoluteErrorTerm(ErrorTerm):
    @property
    def error(self):
        return self._first.error + self._second.error


class Sum(AbsoluteErrorTerm):
    symbol = '+'

    @property
    def value(self):
        return self._first.value + self._second.value


class Difference(AbsoluteErrorTerm):
    symbol = '-'

    @property
    def value(self):
        return self._first.value - self._second.value


class RelativeErrorTerm(ErrorTerm):
    @property
    def error(self):
        return abs(self.value * self.relerror)

    @property
    def relerror(self):
        return self._first.relerror + self._second.relerror


class Product(RelativeErrorTerm):
    symbol = '·'

    @property
    def value(self):
        return self._first.value * self._second.value


class Quotient(RelativeErrorTerm):
    symbol = '÷'

    @property
    def value(self):
        return self._first.value / self._second.value


class Power(RelativeErrorTerm):
    symbol = '^'

    def __init__(self, first, second):
        assert isinstance(first, BaseTerm) and isinstance(second, Number)
        self._first = first
        self._second = Value(second)

    @property
    def value(self):
        return self._first.value**self._second.value

    @property
    def relerror(self):
        return self._first.relerror * abs(self._second.value)
