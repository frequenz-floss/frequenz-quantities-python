# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units."""


from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Self, overload

from ._quantity import BaseValueT, NoDefaultConstructible, Quantity

if TYPE_CHECKING:
    from ._percentage import Percentage
    from ._power import Power
    from ._voltage import Voltage


class Current(
    Quantity[BaseValueT],
    metaclass=NoDefaultConstructible,
    exponent_unit_map={
        -3: "mA",
        0: "A",
    },
):
    """A current quantity.

    Objects of this type are wrappers around `float` values and are immutable.

    The constructors accept a single `float` value, the `as_*()` methods return a
    `float` value, and each of the arithmetic operators supported by this type are
    actually implemented using floating-point arithmetic.

    So all considerations about floating-point arithmetic apply to this type as well.
    """

    @classmethod
    def from_amperes(cls, amperes: BaseValueT) -> Self:
        """Initialize a new current quantity.

        Args:
            amperes: The current in amperes.

        Returns:
            A new current quantity.
        """
        return cls._new(amperes)

    @classmethod
    def from_milliamperes(cls, milliamperes: BaseValueT) -> Self:
        """Initialize a new current quantity.

        Args:
            milliamperes: The current in milliamperes.

        Returns:
            A new current quantity.
        """
        return cls._new(milliamperes, exponent=-3)

    def as_amperes(self) -> BaseValueT:
        """Return the current in amperes.

        Returns:
            The current in amperes.
        """
        return self._base_value

    def as_milliamperes(self) -> BaseValueT:
        """Return the current in milliamperes.

        Returns:
            The current in milliamperes.
        """
        return self._base_value * self._base_value.__class__(1e3)

    # See comment for Power.__mul__ for why we need the ignore here.
    @overload  # type: ignore[override]
    def __mul__(self, scalar: BaseValueT, /) -> Self:
        """Scale this current by a scalar.

        Args:
            scalar: The scalar by which to scale this current.

        Returns:
            The scaled current.
        """

    @overload
    def __mul__(self, percent: Percentage[BaseValueT], /) -> Self:
        """Scale this current by a percentage.

        Args:
            percent: The percentage by which to scale this current.

        Returns:
            The scaled current.
        """

    @overload
    def __mul__(self, other: Voltage[BaseValueT], /) -> Power[BaseValueT]:
        """Multiply the current by a voltage to get a power.

        Args:
            other: The voltage.

        Returns:
            The calculated power.
        """

    def __mul__(
        self, other: BaseValueT | Percentage[BaseValueT] | Voltage[BaseValueT], /
    ) -> Self | Power[BaseValueT]:
        """Return a current or power from multiplying this current by the given value.

        Args:
            other: The scalar, percentage or voltage to multiply by.

        Returns:
            A current or power.
        """
        from ._percentage import Percentage  # pylint: disable=import-outside-toplevel
        from ._power import Power  # pylint: disable=import-outside-toplevel
        from ._voltage import Voltage  # pylint: disable=import-outside-toplevel

        match other:
            case float() | Decimal() | Percentage():
                return super().__mul__(other)  # type: ignore[operator]
            case Voltage():
                return Power._new(self._base_value * other._base_value)
            case _:
                return NotImplemented
