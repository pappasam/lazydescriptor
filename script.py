"""Example script to demonstrate cool usage of this tool."""

from reactivetools import RA, rattr, rdataclass, rproperty


@rdataclass
class Dependent2:
    """Testing class for lazy values.

    Note: this also works for dataclasses. Just remove the "init" method and
    add @dataclasses.dataclass.
    """

    my_normal: int
    my_int: RA[int] = rattr()

    @rproperty(my_int)
    def add_numbers(self) -> int:
        """Docstring to stop complaints."""
        print("Dependent2: ADD NUMBERS")
        return self.my_normal + self.my_int


@rdataclass
class Dependent:
    """Testing class for lazy values.

    Note: this also works for dataclasses. Just remove the "init" method and
    add @dataclasses.dataclass.
    """

    my_normal: int
    my_int: RA[int] = rattr()
    my_dep: RA[Dependent2] = rattr()

    @rproperty(my_int, my_dep)
    def add_numbers(self) -> int:
        """Docstring to stop complaints."""
        print("Dependent: ADD NUMBERS")
        return self.my_normal + self.my_int + self.my_dep.add_numbers


@rdataclass
class Parent:
    """Testing class for lazy values.

    Note: this also works for dataclasses. Just remove the "init" method and
    add @dataclasses.dataclass.
    """

    my_normal: int
    my_int: RA[int] = rattr()
    my_dep: RA[Dependent] = rattr()

    @rproperty(my_int, my_dep)
    def add_numbers(self) -> int:
        """Docstring to stop complaints."""
        print("Parent: ADD NUMBERS")
        return self.my_normal + self.my_int + self.my_dep.add_numbers


a = Dependent2(my_normal=2, my_int=1000)
d = Dependent(my_normal=1, my_int=10, my_dep=a)
p = Parent(my_normal=2, my_int=20, my_dep=d)

print("start")
print(p.add_numbers)
print(p.add_numbers)
print(p.add_numbers)
print("1....")
d.my_int = 1000
print(d.my_int)
d.my_int = 2000
print(d.my_int)
print(p.add_numbers)
print(p.add_numbers)
print(p.add_numbers)
print("2....")
a.my_int = 12
print(a.my_int)
print(a.my_int)
print(a.my_int)
print(p.add_numbers)
print(p.add_numbers)
print(p.add_numbers)
