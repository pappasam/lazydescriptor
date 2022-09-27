import inspect
from typing import Callable, Generic, Optional, TypeVar, Union, overload

__all__ = ["Lazy", "LazyOpt", "LazyDesc", "LazyDescOpt", "lazy"]

_SENTINEL = object()

T = TypeVar("T")


class LazyDesc(Generic[T]):
    """A lazy data descriptor.

    Contains a few more things for mypy
    """

    @overload
    def __init__(self, *, default: "Lazy[T]") -> None:
        ...

    @overload
    def __init__(self) -> None:
        ...

    def __init__(self, *, default=_SENTINEL) -> None:
        self._lazy = isinstance(default, LazyDesc)
        self._value = default

    def set_callable_value(self, value: Callable[[], T]) -> None:
        """Function to set the value manually to a callable."""
        if not callable(value) or len(inspect.signature(value).parameters) > 0:
            raise TypeError("Must be a callable with 0 parameters")
        self._lazy = True
        self._value = value

    def __call__(self) -> T:
        return self._value()  # type: ignore

    def __get__(self, obj, objtype=None) -> T:
        if obj is None:
            return self._value  # type: ignore
        if self._value is _SENTINEL:
            raise ValueError("Value should not be the sentinel")
        if self._lazy:
            self._value = self._value()  # type: ignore
            self._lazy = False
        return self._value  # type: ignore

    def __set__(self, obj, value: "Lazy[T]") -> None:
        self._lazy = isinstance(value, LazyDesc)
        self._value = value


class LazyDescOpt(LazyDesc[Optional[T]]):
    def __init__(self) -> None:
        super().__init__(default=None)


Lazy = Union[T, LazyDesc[T]]
LazyOpt = Union[T, LazyDesc[Optional[T]]]


def lazy(value: Callable[[], T]) -> LazyDesc[T]:
    """Get a lazy thing, setting a value."""
    instance: LazyDesc[T] = LazyDesc()
    instance.set_callable_value(value)
    return instance
