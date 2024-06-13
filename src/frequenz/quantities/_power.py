# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units."""


from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Self, overload

from ._quantity import NoDefaultConstructible, Quantity

if TYPE_CHECKING:
    from ._current import Current
    from ._energy import Energy
    from ._percentage import Percentage
    from ._voltage import Voltage


class Power(
    Quantity,
    metaclass=NoDefaultConstructible,
    exponent_unit_map={
        -3: "mW",
        0: "W",
        3: "kW",
        6: "MW",
    },
):
    """A power quantity.

    Objects of this type are wrappers around `float` values and are immutable.

    The constructors accept a single `float` value, the `as_*()` methods return a
    `float` value, and each of the arithmetic operators supported by this type are
    actually implemented using floating-point arithmetic.

    So all considerations about floating-point arithmetic apply to this type as well.
    """

    @classmethod
    def from_watts(cls, watts: float) -> Self:
        """Initialize a new power quantity.

        Args:
            watts: The power in watts.

        Returns:
            A new power quantity.
        """
        return cls._new(watts)

    @classmethod
    def from_milliwatts(cls, milliwatts: float) -> Self:
        """Initialize a new power quantity.

        Args:
            milliwatts: The power in milliwatts.

        Returns:
            A new power quantity.
        """
        return cls._new(milliwatts, exponent=-3)

    @classmethod
    def from_kilowatts(cls, kilowatts: float) -> Self:
        """Initialize a new power quantity.

        Args:
            kilowatts: The power in kilowatts.

        Returns:
            A new power quantity.
        """
        return cls._new(kilowatts, exponent=3)

    @classmethod
    def from_megawatts(cls, megawatts: float) -> Self:
        """Initialize a new power quantity.

        Args:
            megawatts: The power in megawatts.

        Returns:
            A new power quantity.
        """
        return cls._new(megawatts, exponent=6)

    def as_watts(self) -> float:
        """Return the power in watts.

        Returns:
            The power in watts.
        """
        return self._base_value

    def as_kilowatts(self) -> float:
        """Return the power in kilowatts.

        Returns:
            The power in kilowatts.
        """
        return self._base_value / 1e3

    def as_megawatts(self) -> float:
        """Return the power in megawatts.

        Returns:
            The power in megawatts.
        """
        return self._base_value / 1e6

    # We need the ignore here because otherwise mypy will give this error:
    # > Overloaded operator methods can't have wider argument types in overrides
    # The problem seems to be when the other type implements an **incompatible**
    # __rmul__ method, which is not the case here, so we should be safe.
    # Please see this example:
    # https://github.com/python/mypy/blob/c26f1297d4f19d2d1124a30efc97caebb8c28616/test-data/unit/check-overloading.test#L4738C1-L4769C55
    # And a discussion in a mypy issue here:
    # https://github.com/python/mypy/issues/4985#issuecomment-389692396
    @overload  # type: ignore[override]
    def __mul__(self, scalar: float, /) -> Self:
        """Scale this power by a scalar.

        Args:
            scalar: The scalar by which to scale this power.

        Returns:
            The scaled power.
        """

    @overload
    def __mul__(self, percent: Percentage, /) -> Self:
        """Scale this power by a percentage.

        Args:
            percent: The percentage by which to scale this power.

        Returns:
            The scaled power.
        """

    @overload
    def __mul__(self, other: timedelta, /) -> Energy:
        """Return an energy from multiplying this power by the given duration.

        Args:
            other: The duration to multiply by.

        Returns:
            The calculated energy.
        """

    def __mul__(self, other: float | Percentage | timedelta, /) -> Self | Energy:
        """Return a power or energy from multiplying this power by the given value.

        Args:
            other: The scalar, percentage or duration to multiply by.

        Returns:
            A power or energy.
        """
        from ._energy import Energy  # pylint: disable=import-outside-toplevel
        from ._percentage import Percentage  # pylint: disable=import-outside-toplevel

        match other:
            case float() | Percentage():
                return super().__mul__(other)
            case timedelta():
                return Energy._new(self._base_value * other.total_seconds() / 3600.0)
            case _:
                return NotImplemented

    # See the comment for Power.__mul__ for why we need the ignore here.
    @overload  # type: ignore[override]
    def __truediv__(self, other: float, /) -> Self:
        """Divide this power by a scalar.

        Args:
            other: The scalar to divide this power by.

        Returns:
            The divided power.
        """

    @overload
    def __truediv__(self, other: Self, /) -> float:
        """Return the ratio of this power to another.

        Args:
            other: The other power.

        Returns:
            The ratio of this power to another.
        """

    @overload
    def __truediv__(self, current: Current, /) -> Voltage:
        """Return a voltage from dividing this power by the given current.

        Args:
            current: The current to divide by.

        Returns:
            A voltage from dividing this power by the a current.
        """

    @overload
    def __truediv__(self, voltage: Voltage, /) -> Current:
        """Return a current from dividing this power by the given voltage.

        Args:
            voltage: The voltage to divide by.

        Returns:
            A current from dividing this power by a voltage.
        """

    def __truediv__(
        self, other: float | Self | Current | Voltage, /
    ) -> Self | float | Voltage | Current:
        """Return a current or voltage from dividing this power by the given value.

        Args:
            other: The scalar, power, current or voltage to divide by.

        Returns:
            A current or voltage from dividing this power by the given value.
        """
        from ._current import Current  # pylint: disable=import-outside-toplevel
        from ._voltage import Voltage  # pylint: disable=import-outside-toplevel

        match other:
            case float():
                return super().__truediv__(other)
            case Power():
                return self._base_value / other._base_value
            case Current():
                return Voltage._new(self._base_value / other._base_value)
            case Voltage():
                return Current._new(self._base_value / other._base_value)
            case _:
                return NotImplemented
