"""Test lazyfield."""

from lazyfield import Lazy, LazyField, lazy, lazyfield, lazymethod

# pylint: disable=comparison-with-callable
# pylint: disable=too-few-public-methods


def _return_world() -> str:
    """My cool function."""
    print("RETURN WORLD", end="")
    return "world"


class MyTestClass:
    """Testing class for lazy values."""

    my_normal: int
    my_int: LazyField[int] = lazyfield()
    my_str: LazyField[str] = lazyfield()
    my_list: LazyField[list[str]] = lazyfield()

    def __init__(
        self,
        my_normal: int,
        my_int: Lazy[int],
        my_str: Lazy[str],
        my_list: Lazy[list[str]],
    ) -> None:
        self.my_normal = my_normal
        self.my_int = my_int
        self.my_str = my_str
        self.my_list = my_list

    @lazymethod(my_int)
    def add_numbers(self) -> int:
        """Docstring to stop complaints."""
        print("ADD NUMBERS", end="")
        return self.my_normal + self.my_int


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

    # Test method doesn't run again
    result = TEST1.add_numbers
    captured = capsys.readouterr()
    assert captured.out == ""
    assert result == 25

    # Modify dependency, and see if it runs again
    TEST1.my_int = 13
    result = TEST1.add_numbers
    captured = capsys.readouterr()
    assert captured.out == "ADD NUMBERS"
    assert result == 26

    # Now make sure it doesn't run again, but result is cached
    result = TEST1.add_numbers
    captured = capsys.readouterr()
    assert captured.out == ""
    assert result == 26

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
