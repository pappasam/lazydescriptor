"""Test lazyfield."""
from dataclasses import dataclass

from lazyfield import Lazy, lazy, lazyfield


def _add_numbers(_test: "MyTestClass") -> int:
    print("ADD NUMBERS", end="")
    return _test.my_normal + _test.my_int


def _return_world() -> str:
    print("RETURN WORLD", end="")
    return "world"


@dataclass
class MyTestClass:
    """Testing class for lazy values."""

    my_normal: int
    my_int: Lazy[int] = lazyfield()
    my_str: Lazy[str] = lazyfield()
    my_list: Lazy[list[str]] = lazyfield()
    add_numbers: Lazy[int] = lazyfield(_add_numbers)


TEST1 = MyTestClass(
    my_normal=13,
    my_int=lazy(lambda: 12),
    my_str=lazy(_return_world),
    my_list=lazy(lambda: [str(i) for i in range(10)]),
)

TEST2 = MyTestClass(
    my_normal=13,
    my_int=12,
    my_str=lazy(lambda: "hello"),
    my_list=lazy(lambda: [str(i) for i in range(10)]),
)


def test_all(capsys):
    """Test all methods."""

    # Test method
    result = TEST1.add_numbers
    captured = capsys.readouterr()
    assert captured.out == "ADD NUMBERS"
    assert result == 25

    # Test method runs again
    result = TEST1.add_numbers
    captured = capsys.readouterr()
    assert captured.out == "ADD NUMBERS"
    assert result == 25

    # Test function
    result = TEST1.my_str
    captured = capsys.readouterr()
    assert captured.out == "RETURN WORLD"
    assert result == "world"

    # Test function does not run again
    result = TEST1.my_str
    captured = capsys.readouterr()
    assert captured.out == ""
    assert result == "world"
