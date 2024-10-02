# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units."""


from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, NoReturn, Self, overload

if TYPE_CHECKING:
    from ._percentage import Percentage


class Quantity:
    """A quantity with a unit.

    Quantities try to behave like float and are also immutable.
    """

    _base_value: float
    """The value of this quantity in the base unit."""

    _exponent_unit_map: dict[int, str] | None = None
    """A mapping from the exponent of the base unit to the unit symbol.

    If None, this quantity has no unit.  None is possible only when using the base
    class.  Sub-classes must define this.
    """

    def __init__(self, value: float, exponent: int = 0) -> None:
        """Initialize a new quantity.

        Args:
            value: The value of this quantity in a given exponent of the base unit.
            exponent: The exponent of the base unit the given value is in.
        """
        self._base_value = value * 10.0**exponent

    @classmethod
    def _new(cls, value: float, *, exponent: int = 0) -> Self:
        """Instantiate a new quantity subclass instance.

        Args:
            value: The value of this quantity in a given exponent of the base unit.
            exponent: The exponent of the base unit the given value is in.

        Returns:
            A new quantity subclass instance.
        """
        self = cls.__new__(cls)
        self._base_value = value * 10.0**exponent
        return self

    def __init_subclass__(cls, exponent_unit_map: dict[int, str]) -> None:
        """Initialize a new subclass of Quantity.

        Args:
            exponent_unit_map: A mapping from the exponent of the base unit to the unit
                symbol.

        Raises:
            ValueError: If the given exponent_unit_map does not contain a base unit
                (exponent 0).
        """
        if 0 not in exponent_unit_map:
            raise ValueError("Expected a base unit for the type (for exponent 0)")
        cls._exponent_unit_map = exponent_unit_map
        super().__init_subclass__()

    _zero_cache: dict[type, Quantity] = {}
    """Cache for zero singletons.

    This is a workaround for mypy getting confused when using @functools.cache and
    @classmethod combined with returning Self. It believes the resulting type of this
    method is Self and complains that members of the actual class don't exist in Self,
    so we need to implement the cache ourselves.
    """

    @classmethod
    def zero(cls) -> Self:
        """Return a quantity with value 0.0.

        Returns:
            A quantity with value 0.0.
        """
        _zero = cls._zero_cache.get(cls, None)
        if _zero is None:
            _zero = cls.__new__(cls)
            _zero._base_value = 0.0
            cls._zero_cache[cls] = _zero
        assert isinstance(_zero, cls)
        return _zero

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Return a quantity from a string representation.

        Args:
            string: The string representation of the quantity.

        Returns:
            A quantity object with the value given in the string.

        Raises:
            ValueError: If the string does not match the expected format.

        """
        split_string = string.split(" ")

        if len(split_string) != 2:
            raise ValueError(
                f"Expected a string of the form 'value unit', got {string}"
            )

        assert cls._exponent_unit_map is not None
        exp_map = cls._exponent_unit_map

        for exponent, unit in exp_map.items():
            if unit == split_string[1]:
                instance = cls.__new__(cls)
                try:
                    instance._base_value = float(split_string[0]) * 10**exponent
                except ValueError as error:
                    raise ValueError(f"Failed to parse string '{string}'.") from error

                return instance

        raise ValueError(f"Unknown unit {split_string[1]}")

    @property
    def base_value(self) -> float:
        """Return the value of this quantity in the base unit.

        Returns:
            The value of this quantity in the base unit.
        """
        return self._base_value

    def __round__(self, ndigits: int | None = None) -> Self:
        """Round this quantity to the given number of digits.

        Args:
            ndigits: The number of digits to round to.

        Returns:
            The rounded quantity.
        """
        return self._new(round(self._base_value, ndigits))

    def __pos__(self) -> Self:
        """Return this quantity.

        Returns:
            This quantity.
        """
        return self

    def __mod__(self, other: Self) -> Self:
        """Return the remainder of this quantity and another.

        Args:
            other: The other quantity.

        Returns:
            The remainder of this quantity and another.
        """
        return self._new(self._base_value % other._base_value)

    @property
    def base_unit(self) -> str | None:
        """Return the base unit of this quantity.

        None if this quantity has no unit.

        Returns:
            The base unit of this quantity.
        """
        if not self._exponent_unit_map:
            return None
        return self._exponent_unit_map[0]

    def isnan(self) -> bool:
        """Return whether this quantity is NaN.

        Returns:
            Whether this quantity is NaN.
        """
        return math.isnan(self._base_value)

    def isinf(self) -> bool:
        """Return whether this quantity is infinite.

        Returns:
            Whether this quantity is infinite.
        """
        return math.isinf(self._base_value)

    def isclose(self, other: Self, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
        """Return whether this quantity is close to another.

        Args:
            other: The quantity to compare to.
            rel_tol: The relative tolerance.
            abs_tol: The absolute tolerance.

        Returns:
            Whether this quantity is close to another.
        """
        return math.isclose(
            self._base_value,
            other._base_value,  # pylint: disable=protected-access
            rel_tol=rel_tol,
            abs_tol=abs_tol,
        )

    def __repr__(self) -> str:
        """Return a representation of this quantity.

        Returns:
            A representation of this quantity.
        """
        return f"{type(self).__name__}(value={self._base_value}, exponent=0)"

    def __str__(self) -> str:
        """Return a string representation of this quantity.

        Returns:
            A string representation of this quantity.
        """
        return self.__format__("")

    # pylint: disable=too-many-branches
    def __format__(self, __format_spec: str) -> str:
        """Return a formatted string representation of this quantity.

        If specified, must be of this form: `[0].{precision}`.  If a 0 is not given, the
        trailing zeros will be omitted.  If no precision is given, the default is 3.

        The returned string will use the unit that will result in the maximum precision,
        based on the magnitude of the value.

        Example:
            ```python
            from frequenz.quantities import Current
            c = Current.from_amperes(0.2345)
            assert f"{c:.2}" == "234.5 mA"
            c = Current.from_amperes(1.2345)
            assert f"{c:.2}" == "1.23 A"
            c = Current.from_milliamperes(1.2345)
            assert f"{c:.6}" == "1.2345 mA"
            ```

        Args:
            __format_spec: The format specifier.

        Returns:
            A string representation of this quantity.

        Raises:
            ValueError: If the given format specifier is invalid.
        """
        keep_trailing_zeros = False
        if __format_spec != "":
            fspec_parts = __format_spec.split(".")
            if (
                len(fspec_parts) != 2
                or fspec_parts[0] not in ("", "0")
                or not fspec_parts[1].isdigit()
            ):
                raise ValueError(
                    "Invalid format specifier. Must be empty or `[0].{precision}`"
                )
            if fspec_parts[0] == "0":
                keep_trailing_zeros = True
            precision = int(fspec_parts[1])
        else:
            precision = 3
        if not self._exponent_unit_map:
            return f"{self._base_value:.{precision}f}"

        if math.isinf(self._base_value) or math.isnan(self._base_value):
            return f"{self._base_value} {self._exponent_unit_map[0]}"

        if abs_value := abs(self._base_value):
            precision_pow = 10 ** (precision)
            # Prevent numbers like 999.999999 being rendered as 1000 V
            # instead of 1 kV.
            # This could happen because the str formatting function does
            # rounding as well.
            # This is an imperfect solution that works for _most_ cases.
            # isclose parameters were chosen according to the observed cases
            if math.isclose(abs_value, precision_pow, abs_tol=1e-4, rel_tol=0.01):
                # If the value is close to the precision, round it
                exponent = math.ceil(math.log10(precision_pow))
            else:
                exponent = math.floor(math.log10(abs_value))
        else:
            exponent = 0

        unit_place = exponent - exponent % 3
        if unit_place < min(self._exponent_unit_map):
            unit = self._exponent_unit_map[min(self._exponent_unit_map.keys())]
            unit_place = min(self._exponent_unit_map)
        elif unit_place > max(self._exponent_unit_map):
            unit = self._exponent_unit_map[max(self._exponent_unit_map.keys())]
            unit_place = max(self._exponent_unit_map)
        else:
            unit = self._exponent_unit_map[unit_place]

        value_str = f"{self._base_value / 10 ** unit_place:.{precision}f}"

        if value_str in ("-0", "0"):
            stripped = value_str
        else:
            stripped = value_str.rstrip("0").rstrip(".")

        if not keep_trailing_zeros:
            value_str = stripped
        unit_str = unit if stripped not in ("-0", "0") else self._exponent_unit_map[0]
        return f"{value_str} {unit_str}"

    def __add__(self, other: Self) -> Self:
        """Return the sum of this quantity and another.

        Args:
            other: The other quantity.

        Returns:
            The sum of this quantity and another.
        """
        if not type(other) is type(self):
            return NotImplemented
        summe = type(self).__new__(type(self))
        summe._base_value = self._base_value + other._base_value
        return summe

    def __sub__(self, other: Self) -> Self:
        """Return the difference of this quantity and another.

        Args:
            other: The other quantity.

        Returns:
            The difference of this quantity and another.
        """
        if not type(other) is type(self):
            return NotImplemented
        difference = type(self).__new__(type(self))
        difference._base_value = self._base_value - other._base_value
        return difference

    @overload
    def __mul__(self, scalar: float, /) -> Self:
        """Scale this quantity by a scalar.

        Args:
            scalar: The scalar by which to scale this quantity.

        Returns:
            The scaled quantity.
        """

    @overload
    def __mul__(self, percent: Percentage, /) -> Self:
        """Scale this quantity by a percentage.

        Args:
            percent: The percentage by which to scale this quantity.

        Returns:
            The scaled quantity.
        """

    def __mul__(self, value: float | Percentage, /) -> Self:
        """Scale this quantity by a scalar or percentage.

        Args:
            value: The scalar or percentage by which to scale this quantity.

        Returns:
            The scaled quantity.
        """
        from ._percentage import Percentage  # pylint: disable=import-outside-toplevel

        match value:
            case float():
                return type(self)._new(self._base_value * value)
            case Percentage():
                return type(self)._new(self._base_value * value.as_fraction())
            case _:
                return NotImplemented

    @overload
    def __truediv__(self, other: float, /) -> Self:
        """Divide this quantity by a scalar.

        Args:
            other: The scalar or percentage to divide this quantity by.

        Returns:
            The divided quantity.
        """

    @overload
    def __truediv__(self, other: Self, /) -> float:
        """Return the ratio of this quantity to another.

        Args:
            other: The other quantity.

        Returns:
            The ratio of this quantity to another.
        """

    def __truediv__(self, value: float | Self, /) -> Self | float:
        """Divide this quantity by a scalar or another quantity.

        Args:
            value: The scalar or quantity to divide this quantity by.

        Returns:
            The divided quantity or the ratio of this quantity to another.
        """
        match value:
            case float():
                return type(self)._new(self._base_value / value)
            case Quantity() if type(value) is type(self):
                return self._base_value / value._base_value
            case _:
                return NotImplemented

    def __gt__(self, other: Self) -> bool:
        """Return whether this quantity is greater than another.

        Args:
            other: The other quantity.

        Returns:
            Whether this quantity is greater than another.
        """
        if not type(other) is type(self):
            return NotImplemented
        return self._base_value > other._base_value

    def __ge__(self, other: Self) -> bool:
        """Return whether this quantity is greater than or equal to another.

        Args:
            other: The other quantity.

        Returns:
            Whether this quantity is greater than or equal to another.
        """
        if not type(other) is type(self):
            return NotImplemented
        return self._base_value >= other._base_value

    def __lt__(self, other: Self) -> bool:
        """Return whether this quantity is less than another.

        Args:
            other: The other quantity.

        Returns:
            Whether this quantity is less than another.
        """
        if not type(other) is type(self):
            return NotImplemented
        return self._base_value < other._base_value

    def __le__(self, other: Self) -> bool:
        """Return whether this quantity is less than or equal to another.

        Args:
            other: The other quantity.

        Returns:
            Whether this quantity is less than or equal to another.
        """
        if not type(other) is type(self):
            return NotImplemented
        return self._base_value <= other._base_value

    def __eq__(self, other: object) -> bool:
        """Return whether this quantity is equal to another.

        Args:
            other: The other quantity.

        Returns:
            Whether this quantity is equal to another.
        """
        if not type(other) is type(self):
            return NotImplemented
        # The above check ensures that both quantities are the exact same type, because
        # `isinstance` returns true for subclasses and superclasses.  But the above check
        # doesn't help mypy identify the type of other,  so the below line is necessary.
        assert isinstance(other, self.__class__)
        return self._base_value == other._base_value

    def __neg__(self) -> Self:
        """Return the negation of this quantity.

        Returns:
            The negation of this quantity.
        """
        negation = type(self).__new__(type(self))
        negation._base_value = -self._base_value
        return negation

    def __abs__(self) -> Self:
        """Return the absolute value of this quantity.

        Returns:
            The absolute value of this quantity.
        """
        absolute = type(self).__new__(type(self))
        absolute._base_value = abs(self._base_value)
        return absolute


class NoDefaultConstructible(type):
    """A metaclass that disables the default constructor."""

    def __call__(cls, *_args: Any, **_kwargs: Any) -> NoReturn:
        """Raise a TypeError when the default constructor is called.

        Args:
            *_args: ignored positional arguments.
            **_kwargs: ignored keyword arguments.

        Raises:
            TypeError: Always.
        """
        raise TypeError(
            "Use of default constructor NOT allowed for "
            f"{cls.__module__}.{cls.__qualname__}, "
            f"use one of the `{cls.__name__}.from_*()` methods instead."
        )
