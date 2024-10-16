# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units."""


from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Self, overload

from ._quantity import NoDefaultConstructible, Quantity

if TYPE_CHECKING:
    from ._percentage import Percentage
    from ._power import Power


class Energy(
    Quantity,
    metaclass=NoDefaultConstructible,
    exponent_unit_map={
        0: "Wh",
        3: "kWh",
        6: "MWh",
    },
):
    """An energy quantity.

    Objects of this type are wrappers around `float` values and are immutable.

    The constructors accept a single `float` value, the `as_*()` methods return a
    `float` value, and each of the arithmetic operators supported by this type are
    actually implemented using floating-point arithmetic.

    So all considerations about floating-point arithmetic apply to this type as well.
    """

    @classmethod
    def from_watt_hours(cls, watt_hours: float) -> Self:
        """Initialize a new energy quantity.

        Args:
            watt_hours: The energy in watt hours.

        Returns:
            A new energy quantity.
        """
        return cls._new(watt_hours)

    @classmethod
    def from_kilowatt_hours(cls, kilowatt_hours: float) -> Self:
        """Initialize a new energy quantity.

        Args:
            kilowatt_hours: The energy in kilowatt hours.

        Returns:
            A new energy quantity.
        """
        return cls._new(kilowatt_hours, exponent=3)

    @classmethod
    def from_megawatt_hours(cls, megawatt_hours: float) -> Self:
        """Initialize a new energy quantity.

        Args:
            megawatt_hours: The energy in megawatt hours.

        Returns:
            A new energy quantity.
        """
        return cls._new(megawatt_hours, exponent=6)

    def as_watt_hours(self) -> float:
        """Return the energy in watt hours.

        Returns:
            The energy in watt hours.
        """
        return self._base_value

    def as_kilowatt_hours(self) -> float:
        """Return the energy in kilowatt hours.

        Returns:
            The energy in kilowatt hours.
        """
        return self._base_value / 1e3

    def as_megawatt_hours(self) -> float:
        """Return the energy in megawatt hours.

        Returns:
            The energy in megawatt hours.
        """
        return self._base_value / 1e6

    def __mul__(self, other: float | Percentage) -> Self:
        """Scale this energy by a percentage.

        Args:
            other: The percentage by which to scale this energy.

        Returns:
            The scaled energy.
        """
        from ._percentage import Percentage  # pylint: disable=import-outside-toplevel

        match other:
            case float():
                return self._new(self._base_value * other)
            case Percentage():
                return self._new(self._base_value * other.as_fraction())
            case _:
                return NotImplemented

    # See the comment for Power.__mul__ for why we need the ignore here.
    @overload  # type: ignore[override]
    def __truediv__(self, other: float, /) -> Self:
        """Divide this energy by a scalar.

        Args:
            other: The scalar to divide this energy by.

        Returns:
            The divided energy.
        """

    @overload
    def __truediv__(self, other: Self, /) -> float:
        """Return the ratio of this energy to another.

        Args:
            other: The other energy.

        Returns:
            The ratio of this energy to another.
        """

    @overload
    def __truediv__(self, duration: timedelta, /) -> Power:
        """Return a power from dividing this energy by the given duration.

        Args:
            duration: The duration to divide by.

        Returns:
            A power from dividing this energy by the given duration.
        """

    @overload
    def __truediv__(self, power: Power, /) -> timedelta:
        """Return a duration from dividing this energy by the given power.

        Args:
            power: The power to divide by.

        Returns:
            A duration from dividing this energy by the given power.
        """

    def __truediv__(
        self, other: float | Self | timedelta | Power, /
    ) -> Self | float | Power | timedelta:
        """Return a power or duration from dividing this energy by the given value.

        Args:
            other: The scalar, energy, power or duration to divide by.

        Returns:
            A power or duration from dividing this energy by the given value.
        """
        from ._power import Power  # pylint: disable=import-outside-toplevel

        match other:
            case float():
                return super().__truediv__(other)
            case Energy():
                return self._base_value / other._base_value
            case timedelta():
                return Power._new(self._base_value / (other.total_seconds() / 3600.0))
            case Power():
                return timedelta(
                    seconds=(self._base_value / other._base_value) * 3600.0
                )
            case _:
                return NotImplemented
