import inspect
from typing import Callable, Generic, TypeVar, Union, overload

__all__ = ["Lazy", "LazyDesc", "lazy"]

_SENTINEL = object()

T = TypeVar("T")


class LazyDesc(Generic[T]):
    """A lazy data descriptor.

    Contains a few more things for mypy
    """

    def __init__(self) -> None:
        self._value = _SENTINEL
        self._called = False

    def set_callable_value_manually(self, value: Callable[[], T]) -> None:
        """Function to set the value manually to a callable."""
        if not callable(value) or len(inspect.signature(value).parameters) > 0:
            raise TypeError("Must be a callable with 0 parameters")
        self._called = False
        self._value = value

    def __set_name__(self, owner, name):
        if self._value is not _SENTINEL:
            raise TypeError("Do not set value when using as a descriptor")

    def __call__(self) -> T:
        return self._value()  # type: ignore

    def __get__(self, obj, objtype=None) -> T:
        if obj is None:
            return self._value  # type: ignore
        if not self._called:
            self._value = self._value()  # type: ignore
            self._called = True
        return self._value  # type: ignore

    def __set__(self, obj, value: "Lazy[T]") -> None:
        self._called = not isinstance(value, LazyDesc)
        self._value = value


Lazy = Union[T, LazyDesc[T]]


def lazy(value: Callable[[], T]) -> LazyDesc[T]:
    """Get a lazy thing, setting a value."""
    instance: LazyDesc[T] = LazyDesc()
    instance.set_callable_value_manually(value)
    return instance
