"""The main module."""

from dataclasses import dataclass

from lazydescriptor import Lazy, lazy


@dataclass
class Test:
    """Testing class for lazy values."""

    my_normal: int
    my_int: Lazy[int] = Lazy()
    my_str: Lazy[str] = Lazy()
    my_list: Lazy[list[str]] = Lazy()


test = Test(
    my_normal=13,
    my_int=lazy(lambda: 12),
    my_str=lazy(lambda: "hello"),
    my_list=lazy(lambda: [str(i) for i in range(10)]),
)

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
