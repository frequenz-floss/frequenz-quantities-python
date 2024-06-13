# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units."""


from typing import Self

from ._quantity import NoDefaultConstructible, Quantity


class Percentage(
    Quantity,
    metaclass=NoDefaultConstructible,
    exponent_unit_map={0: "%"},
):
    """A percentage quantity.

    Objects of this type are wrappers around `float` values and are immutable.

    The constructors accept a single `float` value, the `as_*()` methods return a
    `float` value, and each of the arithmetic operators supported by this type are
    actually implemented using floating-point arithmetic.

    So all considerations about floating-point arithmetic apply to this type as well.
    """

    @classmethod
    def from_percent(cls, percent: float) -> Self:
        """Initialize a new percentage quantity from a percent value.

        Args:
            percent: The percent value, normally in the 0.0-100.0 range.

        Returns:
            A new percentage quantity.
        """
        return cls._new(percent)

    @classmethod
    def from_fraction(cls, fraction: float) -> Self:
        """Initialize a new percentage quantity from a fraction.

        Args:
            fraction: The fraction, normally in the 0.0-1.0 range.

        Returns:
            A new percentage quantity.
        """
        return cls._new(fraction * 100)

    def as_percent(self) -> float:
        """Return this quantity as a percentage.

        Returns:
            This quantity as a percentage.
        """
        return self._base_value

    def as_fraction(self) -> float:
        """Return this quantity as a fraction.

        Returns:
            This quantity as a fraction.
        """
        return self._base_value / 100
