# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units."""


from datetime import timedelta
from typing import Self

from ._quantity import NoDefaultConstructible, Quantity


class Frequency(
    Quantity,
    metaclass=NoDefaultConstructible,
    exponent_unit_map={0: "Hz", 3: "kHz", 6: "MHz", 9: "GHz"},
):
    """A frequency quantity.

    Objects of this type are wrappers around `float` values and are immutable.

    The constructors accept a single `float` value, the `as_*()` methods return a
    `float` value, and each of the arithmetic operators supported by this type are
    actually implemented using floating-point arithmetic.

    So all considerations about floating-point arithmetic apply to this type as well.
    """

    @classmethod
    def from_hertz(cls, hertz: float) -> Self:
        """Initialize a new frequency quantity.

        Args:
            hertz: The frequency in hertz.

        Returns:
            A new frequency quantity.
        """
        return cls._new(hertz)

    @classmethod
    def from_kilohertz(cls, kilohertz: float) -> Self:
        """Initialize a new frequency quantity.

        Args:
            kilohertz: The frequency in kilohertz.

        Returns:
            A new frequency quantity.
        """
        return cls._new(kilohertz, exponent=3)

    @classmethod
    def from_megahertz(cls, megahertz: float) -> Self:
        """Initialize a new frequency quantity.

        Args:
            megahertz: The frequency in megahertz.

        Returns:
            A new frequency quantity.
        """
        return cls._new(megahertz, exponent=6)

    @classmethod
    def from_gigahertz(cls, gigahertz: float) -> Self:
        """Initialize a new frequency quantity.

        Args:
            gigahertz: The frequency in gigahertz.

        Returns:
            A new frequency quantity.
        """
        return cls._new(gigahertz, exponent=9)

    def as_hertz(self) -> float:
        """Return the frequency in hertz.

        Returns:
            The frequency in hertz.
        """
        return self._base_value

    def as_kilohertz(self) -> float:
        """Return the frequency in kilohertz.

        Returns:
            The frequency in kilohertz.
        """
        return self._base_value / 1e3

    def as_megahertz(self) -> float:
        """Return the frequency in megahertz.

        Returns:
            The frequency in megahertz.
        """
        return self._base_value / 1e6

    def as_gigahertz(self) -> float:
        """Return the frequency in gigahertz.

        Returns:
            The frequency in gigahertz.
        """
        return self._base_value / 1e9

    def period(self) -> timedelta:
        """Return the period of the frequency.

        Returns:
            The period of the frequency.
        """
        return timedelta(seconds=1.0 / self._base_value)
