import inspect
from typing import Callable, Generic, Optional, TypeVar, Union, overload

__all__ = ["Lazy", "lazyfield", "lazy"]

_NOTHING = object()

T_co = TypeVar("T_co", covariant=True)


class LazyField(Generic[T_co]):
    """A lazy data descriptor.

    Useful with normal objects, dataclasses, and anything else really.
    """

    @overload
    def __init__(self, default: "Lazy[T_co]") -> None:
        ...

    @overload
    def __init__(self) -> None:
        ...

    def __init__(self, default=_NOTHING) -> None:
        self._lazy = isinstance(default, LazyField)
        self._value = default

    def set_callable_value(self, value: Callable[[], T_co]) -> None:
        """Function to set the value manually to a callable."""
        if not callable(value) or len(inspect.signature(value).parameters) > 0:
            raise TypeError("Must be a callable with 0 parameters")
        self._lazy = True
        self._value = value

    def __call__(self) -> T_co:
        return self._value()

    def __get__(self, obj, objtype=None) -> T_co:
        if self._value is _NOTHING:
            raise AttributeError("LazyField not set")
        if obj is None:
            return self._value
        if self._lazy:
            self._value = self._value()
            self._lazy = False
        return self._value

    def __set__(self, obj, value: "Lazy[T_co]") -> None:
        self._lazy = isinstance(value, LazyField)
        self._value = value


Lazy = Union[T_co, LazyField[T_co]]


@overload
def lazyfield() -> LazyField[T_co]:
    ...


@overload
def lazyfield(default: Lazy[T_co]) -> LazyField[T_co]:
    ...


def lazyfield(default=_NOTHING):
    """Create a lazyfield."""
    return LazyField(default)


def lazy(value: Callable[[], T_co]) -> LazyField[T_co]:
    """Get a lazy thing, setting a value."""
    instance: LazyField[T_co] = lazyfield()
    instance.set_callable_value(value)
    return instance
