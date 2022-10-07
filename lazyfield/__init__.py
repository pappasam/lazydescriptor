"""LazyField: lazy evaluation for Python dataclasses and beyond"""

import functools
import inspect
from typing import Any, Callable, Generic, Iterable, TypeVar, Union, overload

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes

__all__ = [
    "LazyField",
    "Lazy",
    "thunk",
    "lazyfield",
    "lazymethod",
]

_NOTHING = object()

T_co = TypeVar("T_co", covariant=True)


class Thunk(Generic[T_co]):
    """Wrap a callable function with no arguments in a class."""

    def __init__(self, value: Callable[[], T_co]) -> None:
        if not callable(value):
            raise ValueError(f"{value} is not callable")
        for pvalue in inspect.signature(value).parameters.values():
            if pvalue.default is inspect.Parameter.empty:
                raise ValueError(f"{value} has required parameters")
        self.value = value


class Method(Generic[T_co]):
    """Wrap a callable function with one argument in a class."""

    def __init__(self, value: Callable[[Any], T_co]) -> None:
        if not callable(value):
            raise ValueError("Is not callable")
        parameters = inspect.signature(value).parameters
        if len(parameters) == 0:
            raise ValueError("Must take at least 1 parameter")
        for i, (pname, pvalue) in enumerate(parameters.items()):
            if i == 0:
                if pname != "self":
                    raise ValueError("First argument must be self")
                if pvalue.default is not inspect.Parameter.empty:
                    raise ValueError("'self' must be a non-default argument")
            elif pvalue.default is inspect.Parameter.empty:
                raise ValueError(
                    f"{value} has required parameters other than self"
                )
        self.value = value


class LazyField(Generic[T_co]):
    """A lazy data descriptor.

    Useful with normal objects, dataclasses, and anything else really.
    """

    @overload
    def __init__(self, default: Union[T_co, Thunk[T_co]]) -> None:
        ...

    @overload
    def __init__(
        self, default: Method[T_co], depends: Iterable["LazyField"]
    ) -> None:
        ...

    @overload
    def __init__(self) -> None:
        ...

    def __init__(self, default=_NOTHING, depends=_NOTHING) -> None:
        self.default = default
        self.depends = [] if depends is _NOTHING else depends
        self.is_thunk = isinstance(default, Thunk)
        self.is_method = isinstance(default, Method)
        self.is_lazy = self.is_thunk or self.is_method
        self.name = "__default"
        self.private_name = "__default_private"
        self.private_name_lazy = "__default_lazy"

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = "_" + name
        self.private_name_lazy = "_" + name + "_lazy"
        if not hasattr(owner, "_relationships"):
            owner._relationships = {}
        for relationship in self.depends:
            if relationship.name == name:
                raise ValueError("A method cannot be related to itself")
            owner._relationships.setdefault(relationship.name, set()).add(name)

    def __get__(self, obj, objtype=None) -> T_co:
        if obj is None:
            if self.default is _NOTHING:
                raise AttributeError("Not set")
            return _NOTHING  # type: ignore
        obj_value = getattr(obj, self.private_name, _NOTHING)
        if obj_value is _NOTHING:
            if self.default is _NOTHING:
                raise AttributeError("Not set")
            if self.is_lazy:
                result = (
                    self.default.value(obj)
                    if self.is_method
                    else self.default.value()
                )
                setattr(obj, self.private_name, result)
                return getattr(obj, self.private_name)
            return self.default
        if isinstance(obj_value, Thunk):
            setattr(obj, self.private_name, obj_value.value())
        if isinstance(obj_value, Method):
            setattr(obj, self.private_name, obj_value.value(obj))
        return getattr(obj, self.private_name)

    def __set__(
        self, obj, value: Union[T_co, Thunk[T_co], Method[T_co]]
    ) -> None:
        setattr(obj, self.private_name, value)
        for dependent in obj._relationships.get(self.name, set()):
            try:
                delattr(obj, dependent)
            except AttributeError:
                pass

    def __delete__(self, obj) -> None:
        delattr(obj, self.private_name)
        for dependent in obj._relationships.get(self.name, set()):
            try:
                delattr(obj, dependent)
            except AttributeError:
                pass


Lazy = Union[T_co, Thunk[T_co], Method[T_co]]


@overload
def lazyfield() -> LazyField[T_co]:
    ...


@overload
def lazyfield(default: Union[T_co, Thunk[T_co]]) -> LazyField[T_co]:
    ...


def lazyfield(default=_NOTHING):
    """Create a lazyfield."""
    return LazyField(default)


def lazymethod(
    *dependencies: LazyField,
) -> Callable[[Callable[[Any], T_co]], LazyField[T_co]]:
    """Lazy method decorator, handling dependencies."""
    for dependency in dependencies:
        if not isinstance(dependency, LazyField):
            raise TypeError(f"{dependency} must be a LazyField")

    def _lazyfield(default: Callable[[Any], T_co]) -> LazyField[T_co]:
        return LazyField(Method(default), dependencies)

    return _lazyfield


def thunk(value: Callable[[], T_co]) -> Thunk[T_co]:
    """Get a thunk, to be used lazily."""
    return Thunk(value)
