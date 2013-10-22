#!/usr/bin/env python3
# -*- coding: utf8 -*-

from decimal import Decimal
from numbers import Number


class BaseTerm:
    def __repr__(self):
        return '({}±{};{:.0%})'.format(
            self.value,
            self.error,
            self.relerror)

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

    def __sub__(self, other):
        return Difference(self, other)

    def __mul__(self, other):
        return Product(self, other)

    def __div__(self, other):
        return Quotient(self, other)

    __truediv__ = __div__

    def __pow__(self, other):
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
        assert isinstance(first, BaseTerm) and isinstance(second, BaseTerm)
        self._first = first
        self._second = second


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
        self._second = second

    @property
    def value(self):
        return self._first.value**self._second

    @property
    def relerror(self):
        return self._first.relerror * abs(self._second)
