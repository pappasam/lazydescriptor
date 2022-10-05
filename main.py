"""The main module."""

from dataclasses import dataclass

from lazyfield import Lazy, lazy, lazyfield

# pylint: disable=invalid-name


def _hello(_test: "Test") -> str:
    print("I ran hello")
    return "I RAN METHOD!!! YOOOO, BRUTHA!"


@dataclass
class Test:
    """Testing class for lazy values."""

    my_normal: int
    my_int: Lazy[int] = lazyfield()
    my_str: Lazy[str] = lazyfield()
    my_list: Lazy[list[str]] = lazyfield()
    hello: Lazy[str] = lazyfield(_hello)

    @lazyfield
    def dep(self) -> int:
        return 13

    @lazyfield
    def use(self) -> int:
        return self.dep + 12


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

print("USE", test2.use)
test2.dep = 200
print("USE", test2.use)

print(test2.my_int)
# print(test2.my_int)
#



def int_func(x: int) -> int:
    """Hello function."""
    print("I ran!", x)
    return x


test.my_int = lazy(lambda: int_func(13))
print(test.my_int)
print(test.my_int)


int_func(test.my_int)

test.my_int = 13

print(test.hello)
print(test.hello)

test.hello = "New Value"
print(test.hello)
print(test.hello)
del test.hello
print(test.hello)
print(test.hello)
print(test)


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
