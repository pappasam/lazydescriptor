"""Reactive tools to make Python a reactive programming experience.

See: <https://en.wikipedia.org/wiki/Reactive_programming>
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Generic, Iterable, TypeVar, Union, overload

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes

__all__ = [
    "RA",
    "RI",
    "rattr",
    "rproperty",
    "thunk",
]

_NOTHING = object()

_EMPTY_SET: set[str] = set()

T_co = TypeVar("T_co", covariant=True)


class Thunk(Generic[T_co]):
    """Wrap, and validate, a callable function with no required arguments."""

    def __init__(self, value: Callable[[], T_co]) -> None:
        if not callable(value):
            raise ValueError(f"{value} is not callable")
        for pvalue in inspect.signature(value).parameters.values():
            if pvalue.default is inspect.Parameter.empty:
                raise ValueError(f"{value} has required parameters")
        self.value = value


class Method(Generic[T_co]):
    """Wrap, and validate, a callable function with one required argument."""

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


# Reactive Input (either realized for deferred (thunk); the input to __set__)
RI = Union[T_co, Thunk[T_co]]


class RA(Generic[T_co]):
    """A data descriptor that manages Reactive class Attributes.

    Useful with normal objects, dataclasses, and anything else really.

    Private names are prepended with a '_$ ', an homage to svelte and an extra
    step that makes the attribute inaccessible without getattr().

    This descriptor performs two semi-weird mutations:
        1. Creates a class variable called '_ra_relationships'. This is a
            dictionary documenting the fields that depend on each field
        2. Creates an instance variable called '_ra_methods_autoset'. This is a
            set containing all method names whose current values represent an
            original computation of the method itself. This is necessary to
            prevent unexpected re-computation for fields that have been
            manually overridden by users. Since dependents can only be methods,
            this trick somehow works!
    """

    @overload
    def __init__(self, default: RI[T_co]) -> None:
        ...

    @overload
    def __init__(self, default: Method[T_co], depends: Iterable[RA]) -> None:
        ...

    @overload
    def __init__(self) -> None:
        ...

    def __init__(self, default=_NOTHING, depends=_NOTHING) -> None:
        self.default = default
        self.depends = [] if depends is _NOTHING else depends
        self.is_thunk = isinstance(default, Thunk)
        self.is_method = isinstance(default, Method)
        self.name = "default"
        self.private_name = "_$ default"

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = "_$ " + name
        if not hasattr(owner, "_ra_relationships"):
            owner._ra_relationships = {}
        for relationship in self.depends:
            if relationship.name == name:
                raise ValueError("A method cannot be related to itself")
            if not relationship.name in owner._ra_relationships:
                owner._ra_relationships[relationship.name] = set()
            owner._ra_relationships[relationship.name].add(name)

    def __get__(self, obj, objtype=None) -> T_co:
        if obj is None:
            if self.default is _NOTHING:
                raise AttributeError("Not set")
            return self.default
        obj_value = getattr(obj, self.private_name, _NOTHING)
        if obj_value is _NOTHING:
            if self.default is _NOTHING:
                raise AttributeError("Not set")
            if self.is_thunk:
                result = self.default.value()
                setattr(obj, self.private_name, result)
                return result
            if self.is_method:
                result = self.default.value(obj)
                setattr(obj, self.private_name, result)
                if not hasattr(obj, "_ra_methods_autoset"):
                    obj._ra_methods_autoset = set()
                obj._ra_methods_autoset.add(self.name)
                return result
            return self.default
        if isinstance(obj_value, Thunk):
            setattr(obj, self.private_name, obj_value.value())
        return getattr(obj, self.private_name)

    def __set__(self, obj, value: RI[T_co]) -> None:
        methods_autoset: set[str] = getattr(
            obj, "_ra_methods_autoset", _EMPTY_SET
        )
        methods_autoset.discard(self.name)
        setattr(obj, self.private_name, value)
        for dependent in obj._ra_relationships.get(self.name, _EMPTY_SET):
            if dependent in methods_autoset:
                try:
                    delattr(obj, dependent)
                except AttributeError:
                    pass

    def __delete__(self, obj) -> None:
        methods_autoset: set[str] = getattr(
            obj, "_ra_methods_autoset", _EMPTY_SET
        )
        methods_autoset.discard(self.name)
        delattr(obj, self.private_name)
        for dependent in obj._ra_relationships.get(self.name, _EMPTY_SET):
            if dependent in methods_autoset:
                try:
                    delattr(obj, dependent)
                except AttributeError:
                    pass


@overload
def rattr() -> RA[T_co]:
    ...


@overload
def rattr(default: RI[T_co]) -> RA[T_co]:
    ...


def rattr(default=_NOTHING):
    """Initialize a reactive attribute.

    Example:
        class MyReactive:
            my_int: RA[int] = rattr()
            my_str_with_default: RA[str] = rattr("my-default")
    """
    return RA(default)


def rproperty(
    *dependencies: RA,
) -> Callable[[Callable[[Any], T_co]], RA[T_co]]:
    """Initialize a reactive method, making it behave a bit like the @property
    decorator. Eg, it does not need to be called.

    Generally useful as a decorator. Example:
        class MyReactive:
            my_int: RA[int] = rattr()

            @rproperty(my_int)
            def add_int(self) -> int:
                return self.my_int + 12
    """
    for dependency in dependencies:
        if not isinstance(dependency, RA):
            raise TypeError(f"{dependency} must be a RA (Reactive Attribute)")

    def _rattr(default: Callable[[Any], T_co]) -> RA[T_co]:
        return RA(Method(default), dependencies)

    return _rattr


def thunk(value: Callable[[], T_co]) -> Thunk[T_co]:
    """Wrap a thunk (no argument function) for rattr.

    See: <https://en.wikipedia.org/wiki/Thunk>
    Example:
        class MyReactive:
            my_int: RA[int] = rattr()
            my_int_with_lazy_default: RA[int] = rattr(thunk(lambda: 12))
    """
    return Thunk(value)
