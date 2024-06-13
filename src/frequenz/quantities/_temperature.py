# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units."""


from typing import Self

from ._quantity import NoDefaultConstructible, Quantity


class Temperature(
    Quantity,
    metaclass=NoDefaultConstructible,
    exponent_unit_map={
        0: "°C",
    },
):
    """A temperature quantity (in degrees Celsius)."""

    @classmethod
    def from_celsius(cls, value: float) -> Self:
        """Initialize a new temperature quantity.

        Args:
            value: The temperature in degrees Celsius.

        Returns:
            A new temperature quantity.
        """
        return cls._new(value)

    def as_celsius(self) -> float:
        """Return the temperature in degrees Celsius.

        Returns:
            The temperature in degrees Celsius.
        """
        return self._base_value
