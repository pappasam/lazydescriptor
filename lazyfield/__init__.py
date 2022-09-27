import inspect
from typing import Callable, Generic, Optional, TypeVar, Union, overload

__all__ = ["Lazy", "LazyField", "lazy"]

_SENTINEL = object()

T = TypeVar("T")


class LazyField(Generic[T]):
    """A lazy data descriptor.

    Useful with normal objects, dataclasses, and anything else really.
    """

    @overload
    def __init__(self, default: "Lazy[T]") -> None:
        ...

    @overload
    def __init__(self) -> None:
        ...

    def __init__(self, default=_SENTINEL) -> None:
        self._lazy = isinstance(default, LazyField)
        self._value = default

    def set_callable_value(self, value: Callable[[], T]) -> None:
        """Function to set the value manually to a callable."""
        if not callable(value) or len(inspect.signature(value).parameters) > 0:
            raise TypeError("Must be a callable with 0 parameters")
        self._lazy = True
        self._value = value

    def __call__(self) -> T:
        return self._value()

    def __get__(self, obj, objtype=None) -> T:
        if self._value is _SENTINEL:
            raise AttributeError("LazyField not set")
        if obj is None:
            return self._value
        if self._lazy:
            self._value = self._value()
            self._lazy = False
        return self._value

    def __set__(self, obj, value: "Lazy[T]") -> None:
        self._lazy = isinstance(value, LazyField)
        self._value = value


Lazy = Union[T, LazyField[T]]


def lazy(value: Callable[[], T]) -> LazyField[T]:
    """Get a lazy thing, setting a value."""
    instance: LazyField[T] = LazyField()
    instance.set_callable_value(value)
    return instance
