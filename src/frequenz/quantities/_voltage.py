# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units."""


from __future__ import annotations

from typing import TYPE_CHECKING, Self, overload

from ._quantity import NoDefaultConstructible, Quantity

if TYPE_CHECKING:
    from ._current import Current
    from ._percentage import Percentage
    from ._power import Power


class Voltage(
    Quantity,
    metaclass=NoDefaultConstructible,
    exponent_unit_map={0: "V", -3: "mV", 3: "kV"},
):
    """A voltage quantity.

    Objects of this type are wrappers around `float` values and are immutable.

    The constructors accept a single `float` value, the `as_*()` methods return a
    `float` value, and each of the arithmetic operators supported by this type are
    actually implemented using floating-point arithmetic.

    So all considerations about floating-point arithmetic apply to this type as well.
    """

    @classmethod
    def from_volts(cls, volts: float) -> Self:
        """Initialize a new voltage quantity.

        Args:
            volts: The voltage in volts.

        Returns:
            A new voltage quantity.
        """
        return cls._new(volts)

    @classmethod
    def from_millivolts(cls, millivolts: float) -> Self:
        """Initialize a new voltage quantity.

        Args:
            millivolts: The voltage in millivolts.

        Returns:
            A new voltage quantity.
        """
        return cls._new(millivolts, exponent=-3)

    @classmethod
    def from_kilovolts(cls, kilovolts: float) -> Self:
        """Initialize a new voltage quantity.

        Args:
            kilovolts: The voltage in kilovolts.

        Returns:
            A new voltage quantity.
        """
        return cls._new(kilovolts, exponent=3)

    def as_volts(self) -> float:
        """Return the voltage in volts.

        Returns:
            The voltage in volts.
        """
        return self._base_value

    def as_millivolts(self) -> float:
        """Return the voltage in millivolts.

        Returns:
            The voltage in millivolts.
        """
        return self._base_value * 1e3

    def as_kilovolts(self) -> float:
        """Return the voltage in kilovolts.

        Returns:
            The voltage in kilovolts.
        """
        return self._base_value / 1e3

    # See comment for Power.__mul__ for why we need the ignore here.
    @overload  # type: ignore[override]
    def __mul__(self, scalar: float, /) -> Self:
        """Scale this voltage by a scalar.

        Args:
            scalar: The scalar by which to scale this voltage.

        Returns:
            The scaled voltage.
        """

    @overload
    def __mul__(self, percent: Percentage, /) -> Self:
        """Scale this voltage by a percentage.

        Args:
            percent: The percentage by which to scale this voltage.

        Returns:
            The scaled voltage.
        """

    @overload
    def __mul__(self, other: Current, /) -> Power:
        """Multiply the voltage by the current to get the power.

        Args:
            other: The current to multiply the voltage with.

        Returns:
            The calculated power.
        """

    def __mul__(self, other: float | Percentage | Current, /) -> Self | Power:
        """Return a voltage or power from multiplying this voltage by the given value.

        Args:
            other: The scalar, percentage or current to multiply by.

        Returns:
            The calculated voltage or power.
        """
        from ._current import Current  # pylint: disable=import-outside-toplevel
        from ._percentage import Percentage  # pylint: disable=import-outside-toplevel
        from ._power import Power  # pylint: disable=import-outside-toplevel

        match other:
            case float() | Percentage():
                return super().__mul__(other)
            case Current():
                return Power._new(self._base_value * other._base_value)
            case _:
                return NotImplemented
