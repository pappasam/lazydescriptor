"""The main module."""

from dataclasses import dataclass

from lazydescriptor import Lazy, LazyField, lazy


@dataclass
class Test:
    """Testing class for lazy values."""

    my_normal: int
    my_int: Lazy[int] = LazyField()
    my_str: Lazy[str] = LazyField()
    my_list: Lazy[list[str]] = LazyField()
    value_with_default: Lazy[int] = LazyDescOpt()


# Note: you can use either the regular type or the lazy function wrapped
# equivalent. Commented out section also works!
test = Test(
    my_normal=13,
    my_int=lazy(lambda: 12),
    # my_int=12,
    my_str=lazy(lambda: "hello"),
    my_list=lazy(lambda: [str(i) for i in range(10)]),
)


def hello(x: int) -> int:
    print("I ran!", x)
    return x


hello(test.my_int)

test.my_int = 13

for _ in range(3):
    print(test.my_int)
for _ in range(3):
    print(test.my_str)
print(test.my_int + 12)
print(test.my_str + "hello")
for _ in range(3):
    print(test.my_list)
print(test.my_normal)
print(test)
