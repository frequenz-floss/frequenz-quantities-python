# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Types for holding quantities with units.

This library provide types for holding quantities with units. The main goal is to avoid
mistakes while working with different types of quantities, for example avoiding adding
a length to a time.

It also prevents mistakes when operating between the same quantity but in different
units, like adding a power in Joules to a power in Watts without converting one of them.

Quantities store the value in a base unit, and then provide methods to get that quantity
as a particular unit. They can only be constructed using special constructors with the
form `Quantity.from_<unit>`, for example
[`Power.from_watts(10.0)`][frequenz.quantities.Power.from_watts].

Internally quantities store values as `float`s, so regular [float issues and limitations
apply](https://docs.python.org/3/tutorial/floatingpoint.html), although some of them are
tried to be mitigated.

Quantities are also immutable, so operations between quantities return a new instance of
the quantity.

This library provides the following types:

- [Current][frequenz.quantities.Current]: A quantity representing an electric current.
- [Energy][frequenz.quantities.Energy]: A quantity representing energy.
- [Frequency][frequenz.quantities.Frequency]: A quantity representing frequency.
- [Percentage][frequenz.quantities.Percentage]: A quantity representing a percentage.
- [Power][frequenz.quantities.Power]: A quantity representing power.
- [Temperature][frequenz.quantities.Temperature]: A quantity representing temperature.
- [Voltage][frequenz.quantities.Voltage]: A quantity representing electric voltage.

Additionally, for each of those types, there is a corresponding marshmallow
field that can be used to serialize and deserialize the quantities using the
[QuantitySchema][frequenz.quantities.marshmallow.QuantitySchema] schema.

There is also the unitless [Quantity][frequenz.quantities.Quantity] class. All
quantities are subclasses of this class and it can be used as a base to create new
quantities. Using the `Quantity` class directly is discouraged, as it doesn't provide
any unit conversion methods.

Example:
    ```python
    from datetime import timedelta
    from frequenz.quantities import Power, Voltage, Current, Energy

    # Create a power quantity
    power = Power.from_watts(230.0)

    # Printing uses a unit to make the string as short as possible
    print(f"Power: {power}")  # Power: 230.0 W
    # The precision can be changed
    print(f"Power: {power:0.3}")  # Power: 230.000 W
    # The conversion methods can be used to get the value in a particular unit
    print(f"Power in MW: {power.as_megawatt()}")  # Power in MW: 0.00023 MW

    # Create a voltage quantity
    voltage = Voltage.from_volts(230.0)

    # Calculate the current
    current = power / voltage
    assert isinstance(current, Current)
    print(f"Current: {current}")  # Current: 1.0 A
    assert current.isclose(Current.from_amperes(1.0))

    # Calculate the energy
    energy = power * timedelta(hours=1)
    assert isinstance(energy, Energy)
    print(f"Energy: {energy}")  # Energy: 230.0 Wh
    print(f"Energy in kWh: {energy.as_kilowatt_hours()}") # Energy in kWh: 0.23

    # Invalid operations are not permitted
    # (when using a type hinting linter like mypy, this will be caught at linting time)
    try:
        power + voltage
    except TypeError as e:
        print(f"Error: {e}")  # Error: unsupported operand type(s) for +: 'Power' and 'Voltage'
    ```
"""


from ._apparent_power import ApparentPower
from ._current import Current
from ._energy import Energy
from ._frequency import Frequency
from ._percentage import Percentage
from ._power import Power
from ._quantity import Quantity
from ._reactive_power import ReactivePower
from ._temperature import Temperature
from ._voltage import Voltage

__all__ = [
    "Current",
    "Energy",
    "Frequency",
    "Percentage",
    "Power",
    "Quantity",
    "ReactivePower",
    "ApparentPower",
    "Temperature",
    "Voltage",
]
