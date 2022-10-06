"""LazyField: lazy evaluation for Python dataclasses and beyond"""

import functools
import inspect
from typing import Any, Callable, Generic, Iterable, TypeVar, Union, overload

__all__ = [
    "Lazy",
    "lazy",
    "lazyfield",
    "lazymethod",
]

_NOTHING = object()

T_co = TypeVar("T_co", covariant=True)


class LazyField(Generic[T_co]):
    """A lazy data descriptor.

    Useful with normal objects, dataclasses, and anything else really.
    """

    @overload
    def __init__(self, default: T_co) -> None:
        ...

    @overload
    def __init__(self, default: Callable[[], T_co]) -> None:
        ...

    @overload
    def __init__(
        self, default: Callable[[Any], T_co], depends: Iterable["Lazy"]
    ) -> None:
        ...

    @overload
    def __init__(self) -> None:
        ...

    def __init__(self, default=_NOTHING, depends=_NOTHING) -> None:
        self._value = default
        self._depends = [] if depends is _NOTHING else depends
        self._method_decorator = (
            callable(default)
            and len(inspect.signature(default).parameters) == 1
        )
        self._lazy = isinstance(default, LazyField) or self._method_decorator
        self.name = "__default"
        self._private_name = "__default_private"
        self._private_name_lazy = "__default_lazy"

    def __set_name__(self, owner, name):
        self.name = name
        self._private_name = "_" + name
        self._private_name_lazy = "_" + name + "_lazy"
        if not hasattr(owner, "_relationships"):
            owner._relationships = {}
        for relationship in self._depends:
            if relationship.name == name:
                raise ValueError("A method cannot be related to itself")
            owner._relationships.setdefault(relationship.name, set()).add(name)

    def __call__(self, obj=None) -> T_co:
        if obj:
            return self._value(obj)
        return self._value()

    def __get__(self, obj, objtype=None) -> T_co:
        if obj is None:
            if self._value is _NOTHING:
                raise AttributeError("Not set")
            return _NOTHING  # type: ignore
        obj_value = getattr(obj, self._private_name, _NOTHING)
        if obj_value is _NOTHING:
            if self._value is _NOTHING:
                raise AttributeError("Not set")
            if self._lazy:
                result = (
                    self._value(obj)
                    if self._method_decorator
                    else self._value()
                )
                setattr(obj, self._private_name, result)  # type: ignore
                setattr(obj, self._private_name_lazy, False)
                return getattr(obj, self._private_name)
            return self._value
        if getattr(obj, self._private_name_lazy, False):
            setattr(obj, self._private_name, obj_value())  # type: ignore
            setattr(obj, self._private_name_lazy, False)
        return getattr(obj, self._private_name)

    def __set__(self, obj, value: "Lazy[T_co]") -> None:
        setattr(obj, self._private_name_lazy, isinstance(value, LazyField))
        setattr(obj, self._private_name, value)
        for dependent in obj._relationships.get(self.name, set()):
            try:
                delattr(obj, dependent)
            except AttributeError:
                pass

    def __delete__(self, obj) -> None:
        delattr(obj, self._private_name)
        delattr(obj, self._private_name_lazy)
        for dependent in obj._relationships.get(self.name, set()):
            try:
                delattr(obj, dependent)
            except AttributeError:
                pass


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


def lazymethod(
    *dependencies: Lazy,
) -> Callable[[Callable[[Any], T_co]], LazyField[T_co]]:
    """Lazy method decorator, handling dependencies."""

    def _lazyfield(default: Callable[[Any], T_co]) -> LazyField[T_co]:
        return LazyField(default, dependencies)

    return _lazyfield


def lazy(value: Callable[[], T_co]) -> LazyField[T_co]:
    """Get a lazy thing, setting a value."""
    if not callable(value) or len(inspect.signature(value).parameters) > 0:
        raise TypeError("Must be a callable with 0 parameters")
    return LazyField(value)
