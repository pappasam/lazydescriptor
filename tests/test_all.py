"""All tests."""

from reactivetools import RA, RI, rattr, rproperty, thunk

# pylint: disable=comparison-with-callable
# pylint: disable=too-few-public-methods


def _return_world() -> str:
    """My cool function."""
    print("RETURN WORLD", end="")
    return "world"


class MyTestClass:
    """Testing class for lazy values.

    Note: this also works for dataclasses. Just remove the "init" method and
    add @dataclasses.dataclass.
    """

    my_normal: int
    my_int: RA[int] = rattr()
    my_str: RA[str] = rattr()
    my_list: RA[list[str]] = rattr()

    def __init__(
        self,
        my_normal: int,
        my_int: RI[int],
        my_str: RI[str],
        my_list: RI[list[str]],
    ) -> None:
        self.my_normal = my_normal
        self.my_int = my_int
        self.my_str = my_str
        self.my_list = my_list

    @rproperty(my_int)
    def add_numbers(self) -> int:
        """Docstring to stop complaints."""
        print("ADD NUMBERS", end="")
        return self.my_normal + self.my_int

    @rproperty(add_numbers)
    def more_adding(self) -> int:
        """Docstring to stop complaints."""
        print("MORE ADDING", end="")
        return self.add_numbers + 12


TEST1 = MyTestClass(
    my_normal=13,
    my_int=thunk(lambda: 12),
    my_str=thunk(_return_world),
    my_list=thunk(lambda: [str(i) for i in range(10)]),
)


TEST2 = MyTestClass(
    my_normal=13,
    my_int=12,
    my_str=thunk(lambda: "hello"),
    my_list=thunk(lambda: [str(i) for i in range(10)]),
)


def test_all(capsys) -> None:
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
    result_str = TEST1.my_str
    captured = capsys.readouterr()
    assert captured.out == "RETURN WORLD"
    assert result_str == "world"

    # Test function does not run again
    result_str = TEST1.my_str
    captured = capsys.readouterr()
    assert captured.out == ""
    assert result_str == "world"

    # Test second function runs
    result = TEST1.more_adding
    captured = capsys.readouterr()
    assert captured.out == "MORE ADDING"
    assert result == 38

    # Here it gets fun. Check to see if we set more_adding explicitly, then set
    # add_numbers explicitly, if we end up getting a recomputation
    TEST1.more_adding = 15
    TEST1.add_numbers = 1
    result = TEST1.more_adding
    captured = capsys.readouterr()
    assert captured.out == ""
    assert result == 15

    # Finally, now we'll delete add_numbers and see if things compute again
    # add_numbers explicitly, if we end up getting a recomputation
    del TEST1.more_adding
    result = TEST1.more_adding
    captured = capsys.readouterr()
    assert captured.out == "MORE ADDING"
    assert result == 13
