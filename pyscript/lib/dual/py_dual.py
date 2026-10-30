# Formula from: https://github.com/BaguetteBunny/dual-lib
# By: BaguetteBunny

from pyscript.core.pysbuiltins import ce, nce
from pyscript.core.utils.decorators import immutable
from pyscript.core.utils.generic import setimuattr, is_environ

from typing import Any, Optional, SupportsIndex

import cmath
import math

np = None
if not is_environ('DUAL_DONT_USE_NUMPY'):
    try:
        import numpy as np
    except:
        pass

EPSILON_SYMBOL = True
HASH_DUAL = 10**6 + 33

def _ln(x) -> float | complex:
    result = cmath.log(x)
    return result.real if result.imag == 0 else result

def _parts(x: 'Any | dual') -> tuple[Any, Any]:
    return (x.real, x.epsilon) if isinstance(x, dual) else (x, 0)

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
                a, b = _parts(real)
                c, _ = _parts(epsilon)
                real, epsilon = a, b + c

        self = super().__new__(cls)
        setimuattr(self, 'real', real)
        setimuattr(self, 'epsilon', epsilon)
        return self

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
        if isinstance(other, dual):
            c, d = other.as_tuple()
            if c == 0 and d == 0:
                return dual(1, 0)
            a, b = self.as_tuple()
            real = a ** c
            return dual(
                real,
                (0 if b == 0 or c == 0 else (b * c * a**(c - 1))) +
                (0 if d == 0 else d * real * _ln(a))
            )
        return dual(1, 0) if other == 0 else dual(self.real**other, self.epsilon * other * self.real**(other - 1))

    def __rpow__(self, other: 'dual | Any') -> 'dual':
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
            self.real != other.real or
            self.epsilon != other.epsilon
        ) if isinstance(other, dual) else (
            self.real != other or
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
            nce(self.real, other.real, **kwargs) or
            nce(self.epsilon, other.epsilon, **kwargs)
        ) if isinstance(other, dual) else (
            nce(self.real, other, **kwargs) or
            nce(self.epsilon, 0, **kwargs)
        )

    def __hash__(self) -> int:
        return hash(self.real) + hash(self.epsilon) * HASH_DUAL

    def __reduce__(self) -> tuple[type['dual'], tuple[Any, Any]]:
        return type(self), self.as_tuple()

    def __neg__(self) -> 'dual':
        return dual(-self.real, -self.epsilon)

    def __pos__(self) -> 'dual':
        return dual(+self.real, +self.epsilon)

    def __bool__(self) -> bool:
        return bool(self.real != 0 or self.epsilon != 0)

    def __int__(self) -> int:
        return int(self.real)

    def __float__(self) -> float:
        return float(self.real)

    def __floor__(self) -> 'dual':
        return dual(math.floor(self.real), 0)

    def __ceil__(self) -> 'dual':
        return dual(math.ceil(self.real), 0)

    def __trunc__(self) -> 'dual':
        return dual(math.trunc(self.real), 0)

    def __round__(self, ndigits: Optional[SupportsIndex] = None) -> 'dual':
        return dual(round(self.real, ndigits), 0)

    def __abs__(self) -> 'dual':
        return dual(abs(self.real), self.epsilon if self.real >= 0 else -self.epsilon)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.real!r}, {self.epsilon!r})'

    def __str__(self) -> str:
        return format(self, '!r')

    def __format__(self, format_spec: str = '') -> str:
        is_repr = format_spec == '!r'
        is_formated = not is_repr and format_spec != ''

        string = ''
        parenthesis = False
        inner_parenthesis = False

        if is_formated or self.real != 0:
            parenthesis = True
            real = repr(self.real) if is_repr else format(self.real, format_spec)
            try:
                sign = ' + ' if self.epsilon >= 0 else ' - '
            except Exception:
                inner_parenthesis = True
                string += f'({real}) + '
            else:
                string += real + sign

        if inner_parenthesis:
            string += f'({repr(self.epsilon) if is_repr else format(self.epsilon, format_spec)})'
        elif is_formated or self.epsilon not in (-1, 1):
            string += repr(abs(self.epsilon)) if is_repr else format(abs(self.epsilon), format_spec)

        string += '\u03b5' if EPSILON_SYMBOL else 'eps'
        return f'({string})' if parenthesis else string

    if np is not None:
        def __array__(self, *args, **kwargs):
            return np.array(self.as_lmatrix(), *args, **kwargs)

    def as_tuple(self) -> tuple[Any, Any]:
        return self.real, self.epsilon

    def as_lmatrix(self, n: int = 2) -> list[list[Any]]:
        return [[self.real if i == j else self.epsilon if (i, j) == (0, 1) else 0 for j in range(n)] for i in range(n)]

    @classmethod
    def from_number(cls, number: Any) -> 'dual':
        return cls(0, number)