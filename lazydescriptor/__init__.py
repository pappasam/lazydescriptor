import inspect
from typing import Callable, Generic, TypeVar

__all__ = ["Lazy", "lazy"]

_SENTINEL = object()

T = TypeVar("T")


class Lazy(Generic[T]):
    """A lazy data descriptor.

    Contains a few more things for mypy
    """

    def __init__(self) -> None:
        self.value = _SENTINEL
        self.called = False

    def __set_name__(self, owner, name):
        if self.value is not _SENTINEL:
            raise TypeError("Do not set value when using as a descriptor")

    def __call__(self) -> T:
        if (
            not callable(self.value)
            or len(inspect.signature(self.value).parameters) > 0
        ):
            raise TypeError("Must be a callable with 0 parameters")
        return self.value()

    def __get__(self, obj, objtype=None) -> T:
        if obj is None:
            return self.value  # type: ignore
        if not self.called:
            self.value = self.value()  # type: ignore
            self.called = True
        return self.value  # type: ignore

    def __set__(self, obj, value: "Lazy[T]") -> None:
        if not callable(value) or len(inspect.signature(value).parameters) > 0:
            raise TypeError("Must be a callable with 0 parameters")
        self.called = False
        self.value = value


def lazy(value: Callable[[], T]) -> Lazy[T]:
    """Get a lazy thing, setting a value."""
    instance: Lazy[T] = Lazy()
    instance.value = value
    return instance
