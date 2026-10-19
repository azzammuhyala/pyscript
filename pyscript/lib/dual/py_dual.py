# Formula from: https://github.com/BaguetteBunny/dual-lib
# By: BaguetteBunny

from pyscript.core.pysbuiltins import ce, nce
from pyscript.core.utils.decorators import immutable
from pyscript.core.utils.generic import setimuattr

from typing import Any

import cmath

EPSILON_SYMBOL = True

def _ln(x) -> float | complex:
    result = cmath.log(x)
    return result.real if isinstance(result, complex) and result.imag == 0 else result

@immutable
class dual:

    __slots__ = ('real', 'epsilon')

    def __new__(cls, *args) -> 'dual':
        match len(args):
            case 0:
                real = epsilon = 0
            case 1:
                real = args[0]
                if isinstance(real, dual):
                    return real
                epsilon = 0
            case _:
                real, epsilon = args

        self = super().__new__(cls)
        setimuattr(self, 'real', real)
        setimuattr(self, 'epsilon', epsilon)
        return self

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.real!r}, {self.epsilon!r})'

    def __str__(self) -> str:
        string = ''
        parenthesis = False
        inner_parenthesis = False

        if self.real != 0:
            parenthesis = True
            try:
                sign = '+' if self.epsilon >= 0 else '-'
            except Exception:
                inner_parenthesis = True
                string += f'({self.real!r})+'
            else:
                string += repr(self.real)
                string += sign

        if inner_parenthesis:
            string += f'({self.epsilon!r})'
        elif self.epsilon != 1 and self.epsilon != -1:
            string += repr(abs(self.epsilon))

        string += '\u03b5' if EPSILON_SYMBOL else 'eps'
        return f'({string})' if parenthesis else string

    def __add__(self, other: 'dual | Any') -> 'dual':
        return dual(
            self.real + other.real,
            self.epsilon + other.epsilon
        ) if isinstance(other, dual) else dual(
            self.real + other,
            self.epsilon
        )

    def __radd__(self, other: 'dual | Any') -> 'dual':
        return dual(
            other.real + self.real,
            other.epsilon + self.epsilon
        ) if isinstance(other, dual) else dual(
            other + self.real,
            self.epsilon
        )

    def __sub__(self, other: 'dual | Any') -> 'dual':
        return dual(
            self.real - other.real,
            self.epsilon - other.epsilon
        ) if isinstance(other, dual) else dual(
            self.real - other,
            self.epsilon
        )

    def __rsub__(self, other: 'dual | Any') -> 'dual':
        return dual(
            other.real - self.real,
            other.epsilon - self.epsilon
        ) if isinstance(other, dual) else dual(
            other - self.real,
            self.epsilon
        )

    def __mul__(self, other: 'dual | Any') -> 'dual':
        return dual(
            self.real * other.real,
            self.real * other.epsilon + self.epsilon * other.real
        ) if isinstance(other, dual) else dual(
            self.real * other,
            self.epsilon * other
        )

    def __rmul__(self, other: 'dual | Any') -> 'dual':
        return dual(
            other.real * self.real,
            other.real * self.epsilon + other.epsilon * self.real
        ) if isinstance(other, dual) else dual(
            other * self.real,
            other * self.epsilon
        )

    def __truediv__(self, other: 'dual | Any') -> 'dual':
        return dual(
            self.real / other.real, 
            (self.epsilon * other.real - self.real * other.epsilon) / other.real**2
        ) if isinstance(other, dual) else dual(
            self.real / other,
            self.epsilon / other
        )

    def __rtruediv__(self, other: 'dual | Any') -> 'dual':
        return other / self if isinstance(other, dual) else dual(
            other / self.real,
            other * -self.epsilon / self.real**2
        )

    def __floordiv__(self, other: 'dual | Any') -> 'dual':
        return dual(
            self.real // other.real,
            0
        ) if isinstance(other, dual) else dual(
            self.real // other,
            0
        )

    def __rfloordiv__(self, other: 'dual | Any') -> 'dual':
        return other // self if isinstance(other, dual) else dual(
            other // self.real,
            0
        )

    def __mod__(self, other: 'dual | Any') -> 'dual':
        return dual(
            self.real % other.real,
            self.epsilon - other.epsilon * (self.real // other.real)
        ) if isinstance(other, dual) else dual(
            self.real % other,
            self.epsilon
        )

    def __rmod__(self, other: 'dual | Any') -> 'dual':
        return other % self if isinstance(other, dual) else dual(
            other % self.real,
            -self.epsilon * (other // self.real)
        )

    def __pow__(self, other: 'dual | Any') -> 'dual':
        return dual(
            real := self.real ** other.real,
            self.epsilon * other.real * self.real**(other.real - 1) + other.epsilon * real * _ln(self.real)
        ) if isinstance(other, dual) else dual(
            self.real**other,
            self.epsilon * other * self.real**(other - 1)
        )

    def  __rpow__(self, other: 'dual | Any') -> 'dual':
        return other**self if isinstance(other, dual) else dual(
            real := other ** self.real,
            self.epsilon * real * _ln(other)
        )

    def __eq__(self, other: 'dual | Any') -> bool | Any:
        return (
            self.real == other.real and
            self.epsilon == other.epsilon
        ) if isinstance(other, dual) else (
            self.real == other and
            self.epsilon == 0
        )

    def __ne__(self, other: 'dual | Any') -> bool | Any:
        return (
            self.real != other.real and
            self.epsilon != other.epsilon
        ) if isinstance(other, dual) else (
            self.real != other and
            self.epsilon != 0
        )

    def __ce__(self, other: 'dual | Any', **kwargs) -> bool | Any:
        return (
            ce(self.real, other.real, **kwargs) and
            ce(self.epsilon, other.epsilon, **kwargs)
        ) if isinstance(other, dual) else (
            ce(self.real, other, **kwargs) and
            ce(self.epsilon, 0, **kwargs)
        )

    def __nce__(self, other: 'dual | Any', **kwargs) -> bool | Any:
        return (
            nce(self.real, other.real, **kwargs) and
            nce(self.epsilon, other.epsilon, **kwargs)
        ) if isinstance(other, dual) else (
            nce(self.real, other, **kwargs) and
            nce(self.epsilon, 0, **kwargs)
        )

    def __neg__(self) -> 'dual':
        return dual(-self.real, -self.epsilon)

    def __pos__(self) -> 'dual':
        return dual(+self.real, +self.epsilon)

    def __bool__(self) -> bool:
        return bool(self.real != 0 and self.epsilon != 0)

    def __int__(self) -> int:
        return int(self.real)

    def __float__(self) -> float:
        return float(self.real)

    def __hash__(self) -> int:
        return hash((type(self), self.real, self.epsilon))

    def __round__(self, ndigits=None) -> 'dual':
        return dual(round(self.real, ndigits), 0)

    def __abs__(self) -> 'dual':
        return dual(abs(self.real), 0)

    def as_tuple(self) -> tuple[Any, Any]:
        return self.real, self.epsilon

    @classmethod
    def from_number(cls, number) -> 'dual':
        return cls(0, number)