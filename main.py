"""The main module."""

from dataclasses import dataclass
from typing import Optional

from lazyfield import Lazy, lazy, lazyfield

# pylint: disable=invalid-name


@dataclass
class Test:
    """Testing class for lazy values."""

    my_normal: int
    my_int: Lazy[int] = lazyfield()
    my_str: Lazy[str] = lazyfield()
    my_list: Lazy[list[str]] = lazyfield()

    @lazyfield
    def hello(self) -> str:
        print("I RAN")
        return "YOOOO, BRUTHA!"


# Note: you can use either the regular type or the lazy function wrapped
# equivalent. Commented out section also works!
test2 = Test(
    my_normal=13,
    my_int=lazy(lambda: 12),
    # my_int=12,
    my_str=lazy(lambda: "world"),
    my_list=lazy(lambda: [str(i) for i in range(10)]),
)
test = Test(
    my_normal=13,
    my_int=lazy(lambda: 12),
    # my_int=12,
    my_str=lazy(lambda: "hello"),
    my_list=lazy(lambda: [str(i) for i in range(10)]),
)


def hello(x: int) -> int:
    """Hello function."""
    print("I ran!", x)
    return x


hello(test.my_int)

test.my_int = 13

print(test.hello)
print(test.hello)

test.hello = "Hello!"
print(test.hello)
print(test.hello)

print("test on test 2", test2.hello)

for _ in range(3):
    print(test.my_int)
for _ in range(3):
    print(test.my_str)
print("CHECKING", test2.my_str)
print(test.my_int + 12)
print(test.my_str + "hello")
for _ in range(3):
    print(test.my_list)
print(test.my_normal)
print(test)
