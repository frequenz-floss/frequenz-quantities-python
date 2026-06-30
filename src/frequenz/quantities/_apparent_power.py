# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Types for holding apparent power quantities with units."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self, overload

from ._quantity import NoDefaultConstructible, Quantity

if TYPE_CHECKING:
    from ._current import Current
    from ._percentage import Percentage
    from ._voltage import Voltage


class ApparentPower(
    Quantity,
    metaclass=NoDefaultConstructible,
    exponent_unit_map={
        -3: "mVA",
        0: "VA",
        3: "kVA",
        6: "MVA",
    },
):
    """An apparent power quantity.

    Objects of this type are wrappers around `float` values and are immutable.

    The constructors accept a single `float` value, the `as_*()` methods return a
    `float` value, and each of the arithmetic operators supported by this type are
    actually implemented using floating-point arithmetic.

    So all considerations about floating-point arithmetic apply to this type as well.
    """

    @classmethod
    def from_volt_amperes(cls, value: float) -> Self:
        """Initialize a new apparent power quantity.

        Args:
            value: The apparent power in volt-amperes (VA).

        Returns:
            A new apparent power quantity.
        """
        return cls._new(value)

    @classmethod
    def from_milli_volt_amperes(cls, mva: float) -> Self:
        """Initialize a new apparent power quantity.

        Args:
            mva: The apparent power in millivolt-amperes (mVA).

        Returns:
            A new apparent power quantity.
        """
        return cls._new(mva, exponent=-3)

    @classmethod
    def from_kilo_volt_amperes(cls, kva: float) -> Self:
        """Initialize a new apparent power quantity.

        Args:
            kva: The apparent power in kilovolt-amperes (kVA).

        Returns:
            A new apparent power quantity.
        """
        return cls._new(kva, exponent=3)

    @classmethod
    def from_mega_volt_amperes(cls, mva: float) -> Self:
        """Initialize a new apparent power quantity.

        Args:
            mva: The apparent power in megavolt-amperes (MVA).

        Returns:
            A new apparent power quantity.
        """
        return cls._new(mva, exponent=6)

    def as_volt_amperes(self) -> float:
        """Return the apparent power in volt-amperes (VA).

        Returns:
            The apparent power in volt-amperes (VA).
        """
        return self._base_value

    def as_milli_volt_amperes(self) -> float:
        """Return the apparent power in millivolt-amperes (mVA).

        Returns:
            The apparent power in millivolt-amperes (mVA).
        """
        return self._base_value * 1e3

    def as_kilo_volt_amperes(self) -> float:
        """Return the apparent power in kilovolt-amperes (kVA).

        Returns:
            The apparent power in kilovolt-amperes (kVA).
        """
        return self._base_value / 1e3

    def as_mega_volt_amperes(self) -> float:
        """Return the apparent power in megavolt-amperes (MVA).

        Returns:
            The apparent power in megavolt-amperes (MVA).
        """
        return self._base_value / 1e6

    @overload
    def __mul__(self, scalar: float, /) -> Self:
        """Scale this apparent power by a scalar.

        Args:
            scalar: The scalar by which to scale this apparent power.

        Returns:
            The scaled apparent power.
        """

    @overload
    def __mul__(self, percent: Percentage, /) -> Self:
        """Scale this apparent power by a percentage.

        Args:
            percent: The percentage by which to scale this apparent power.

        Returns:
            The scaled apparent power.
        """

    def __mul__(self, other: float | Percentage, /) -> Self:
        """Scale this apparent power by a scalar or percentage.

        Args:
            other: The scalar or percentage by which to scale this apparent power.

        Returns:
            The scaled apparent power.
        """
        from ._percentage import Percentage  # pylint: disable=import-outside-toplevel

        match other:
            case float() | Percentage():
                return super().__mul__(other)
            case _:
                return NotImplemented

    # We need the ignore here because otherwise mypy will give this error:
    # > Overloaded operator methods can't have wider argument types in overrides
    # The problem seems to be when the other type implements an **incompatible**
    # __rmul__ method, which is not the case here, so we should be safe.
    # Please see this example:
    # https://github.com/python/mypy/blob/c26f1297d4f19d2d1124a30efc97caebb8c28616/test-data/unit/check-overloading.test#L4738C1-L4769C55
    # And a discussion in a mypy issue here:
    # https://github.com/python/mypy/issues/4985#issuecomment-389692396
    @overload  # type: ignore[override]
    def __truediv__(self, other: float, /) -> Self:
        """Divide this apparent power by a scalar.

        Args:
            other: The scalar to divide this apparent power by.

        Returns:
            The divided apparent power.
        """

    @overload
    def __truediv__(self, other: Self, /) -> float:
        """Return the ratio of this apparent power to another.

        Args:
            other: The other apparent power.

        Returns:
            The ratio of this apparent power to another.
        """

    @overload
    def __truediv__(self, current: Current, /) -> Voltage:
        """Return a voltage from dividing this apparent power by the given current.

        Args:
            current: The current to divide by.

        Returns:
            A voltage from dividing this apparent power by a current.
        """

    @overload
    def __truediv__(self, voltage: Voltage, /) -> Current:
        """Return a current from dividing this apparent power by the given voltage.

        Args:
            voltage: The voltage to divide by.

        Returns:
            A current from dividing this apparent power by a voltage.
        """

    def __truediv__(
        self, other: float | Self | Current | Voltage, /
    ) -> Self | float | Voltage | Current:
        """Return a scaled apparent power, ratio, voltage, or current.

        Args:
            other: The scalar, apparent power, current or voltage to divide by.

        Returns:
            A scaled apparent power, a ratio, a voltage, or a current.
        """
        from ._current import Current  # pylint: disable=import-outside-toplevel
        from ._voltage import Voltage  # pylint: disable=import-outside-toplevel

        match other:
            case float():
                return super().__truediv__(other)
            case ApparentPower():
                return self._base_value / other._base_value
            case Current():
                return Voltage._new(self._base_value / other._base_value)
            case Voltage():
                return Current._new(self._base_value / other._base_value)
            case _:
                return NotImplemented
