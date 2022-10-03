import inspect
from typing import Any, Callable, Generic, Optional, TypeVar, Union, overload

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
        self._value = default
        self._method_decorator = (
            callable(default)
            and len(inspect.signature(default).parameters) == 1
        )
        self._private_name = "default"
        self._private_name_lazy = "default_lazy"

    def __set_name__(self, owner, name):
        self._private_name = "_" + name
        self._private_name_lazy = "_" + name + "_lazy"

    def set_callable_value(self, value: Callable[[], T_co]) -> None:
        """Function to set the value manually to a callable."""
        if not callable(value) or len(inspect.signature(value).parameters) > 0:
            raise TypeError("Must be a callable with 0 parameters")
        self._value = value

    def __call__(self, obj=None) -> T_co:
        if obj:
            return self._value(obj)
        return self._value()

    def __get__(self, obj, objtype=None) -> T_co:
        if obj is None:
            return self._value
        obj_value = getattr(obj, self._private_name, _NOTHING)
        if obj_value is _NOTHING:
            if self._method_decorator:
                return self._value(obj)
            raise AttributeError("LazyField not set")
        obj_lazy = getattr(obj, self._private_name_lazy, False)
        if obj_lazy:
            setattr(obj, self._private_name, obj_value())  # type: ignore
            setattr(obj, self._private_name_lazy, False)
        return getattr(obj, self._private_name)

    def __set__(self, obj, value: "Lazy[T_co]") -> None:
        setattr(obj, self._private_name_lazy, isinstance(value, LazyField))
        setattr(obj, self._private_name, value)

    def __delete__(self, obj) -> None:
        delattr(obj, self._private_name)
        delattr(obj, self._private_name_lazy)


Lazy = Union[T_co, LazyField[T_co]]


@overload
def lazyfield() -> LazyField[T_co]:
    ...


@overload
def lazyfield(default: Callable[[Any], T_co]) -> LazyField[T_co]:
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
