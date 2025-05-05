# License: All rights reserved
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Custom marshmallow fields and schema.

This module provides custom marshmallow fields for quantities and
a [QuantitySchema][frequenz.quantities.experimental.marshmallow.QuantitySchema] class to
be used as base schema for dataclasses containing quantities.

Danger:
    This module contains experimental features for which the API is not yet stable.

    Any module or class in this package may be removed or changed in a future release,
    even in minor or patch releases.
"""

from contextvars import ContextVar
from typing import Any, Type

from marshmallow import Schema, ValidationError
from marshmallow.fields import Field

from .._apparent_power import ApparentPower
from .._current import Current
from .._energy import Energy
from .._frequency import Frequency
from .._percentage import Percentage
from .._power import Power
from .._quantity import Quantity
from .._reactive_power import ReactivePower
from .._temperature import Temperature
from .._voltage import Voltage

serialize_as_string_default: ContextVar[bool] = ContextVar(
    "serialize_as_string_default", default=False
)
"""Context variable to control the default serialization format for quantities.

If True, quantities are serialized as strings with units.
If False, quantities are serialized as floats.

This can be overridden on a per-field basis using the `serialize_as_string`
metadata attribute.
"""


class _QuantityField(Field[Quantity]):
    """Custom field for Quantity objects supporting per-field serialization configuration.

    This class handles serialization and deserialization of ALL Quantity
    subclasses.
    The specific Quantity subclass is determined by the field_type attribute.

    * Deserialization auto-detects the type of deserialization (float or string)
      based on the input type.
    * Serialization uses either the schema's default or the per-field
      configuration found in the metadata.

    We need distinct QuantityField subclasses for each Quantity subclass, so
    they can be used in the TYPE_MAPPING in the `QuantitySchema`.
    Which means this class is not intended to be used directly.

    Instead, we use the specific QuantityField subclasses for each Quantity.
    Each field subclass simply sets the field_type attribute to the corresponding
    Quantity subclass.

    Those subclasses are generated and stored in the QUANTITY_FIELD_CLASSES
    mapping and are used for the TYPE_MAPPING in the `QuantitySchema`.
    """

    field_type: Type[Quantity] | None = None
    """The specific Quantity subclass."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the field."""
        self.serialize_as_string_override = kwargs.pop("serialize_as_string", None)
        super().__init__(*args, **kwargs)

    def _serialize(
        self, value: Quantity | None, attr: str | None, obj: Any, **kwargs: Any
    ) -> Any:
        """Serialize the Quantity object based on per-field configuration."""
        if self.field_type is None or not issubclass(self.field_type, Quantity):
            raise TypeError(
                "field_type must be set to a Quantity subclass in the subclass."
            )
        if value is None:
            return None

        if not isinstance(value, Quantity):
            raise TypeError(
                f"Expected a Quantity object, but got {type(value).__name__}."
            )

        # Determine the serialization format
        default = serialize_as_string_default.get()
        serialize_as_string = (
            self.serialize_as_string_override
            if self.serialize_as_string_override is not None
            else default
        )

        if serialize_as_string:
            # Use the Quantity's native string representation (includes unit)
            return str(value)

        # Serialize as float using the Quantity's base value
        return value.base_value

    def _deserialize(
        self, value: Any, attr: str | None, data: Any, **kwargs: Any
    ) -> Quantity:
        """Deserialize the Quantity object from float or string."""
        if self.field_type is None or not issubclass(self.field_type, Quantity):
            raise TypeError(
                "field_type must be set to a Quantity subclass in the subclass."
            )

        if isinstance(value, str):
            # Use the Quantity's from_string method
            try:
                return self.field_type.from_string(value)
            except Exception as error:  # pylint: disable=broad-except
                raise ValidationError(str(error)) from error
        if isinstance(value, (float, int)):
            try:
                # Use `_new` method for creating instance from base value
                return self.field_type._new(  # pylint: disable=protected-access
                    float(value)
                )
            except Exception as error:  # pylint: disable=broad-except
                raise ValidationError(str(error)) from error

        raise ValidationError("Invalid input type for QuantityField.")


_QUANTITY_SUBCLASSES = [
    ApparentPower,
    Current,
    Energy,
    Frequency,
    Percentage,
    Power,
    ReactivePower,
    Temperature,
    Voltage,
]


class ApparentPowerField(_QuantityField):
    """Custom field for ApparentPower objects."""

    field_type = ApparentPower


class CurrentField(_QuantityField):
    """Custom field for Current objects."""

    field_type = Current


class EnergyField(_QuantityField):
    """Custom field for Energy objects."""

    field_type = Energy


class FrequencyField(_QuantityField):
    """Custom field for Frequency objects."""

    field_type = Frequency


class PercentageField(_QuantityField):
    """Custom field for Percentage objects."""

    field_type = Percentage


class PowerField(_QuantityField):
    """Custom field for Power objects."""

    field_type = Power


class ReactivePowerField(_QuantityField):
    """Custom field for ReactivePower objects."""

    field_type = ReactivePower


class TemperatureField(_QuantityField):
    """Custom field for Temperature objects."""

    field_type = Temperature


class VoltageField(_QuantityField):
    """Custom field for Voltage objects."""

    field_type = Voltage


QUANTITY_FIELD_CLASSES: dict[type[Quantity], type[Field[Any]]] = {
    ApparentPower: ApparentPowerField,
    Current: CurrentField,
    Energy: EnergyField,
    Frequency: FrequencyField,
    Percentage: PercentageField,
    Power: PowerField,
    ReactivePower: ReactivePowerField,
    Temperature: TemperatureField,
    Voltage: VoltageField,
}
"""Mapping of Quantity subclasses to their corresponding QuantityField subclasses.

This mapping is used in the `QuantitySchema` to determine the correct field
class for each Quantity subclass.

The keys are Quantity subclasses (e.g., Percentage, Energy) and the values are
the corresponding QuantityField subclasses.
"""


class QuantitySchema(Schema):
    """A schema for quantities.

    Example usage:

    ```python
    from dataclasses import dataclass, field
    from marshmallow_dataclass import class_schema
    from marshmallow.validate import Range
    from frequenz.quantities import Percentage
    from frequenz.quantities.experimental.marshmallow import (
        QuantitySchema,
        serialize_as_string_default,
    )

    @dataclass
    class Config:
        percentage_always_as_string: Percentage = field(
            default_factory=lambda: Percentage.from_percent(25.0),
            metadata={
                "metadata": {
                    "description": "A percentage field",
                },
                "validate": Range(Percentage.zero(), Percentage.from_percent(100.0)),
                "serialize_as_string": True,
            },
        )

        percentage_always_as_float: Percentage = field(
            default_factory=lambda: Percentage.from_percent(25.0),
            metadata={
                "metadata": {
                    "description": "A percentage field",
                },
                "validate": Range(Percentage.zero(), Percentage.from_percent(100.0)),
                "serialize_as_string": False,
            },
        )

        percentage_serialized_as_schema_default: Percentage = field(
            default_factory=lambda: Percentage.from_percent(25.0),
            metadata={
                "metadata": {
                    "description": "A percentage field",
                },
                "validate": Range(Percentage.zero(), Percentage.from_percent(100.0)),
            },
        )

    config_obj = Config()
    Schema = class_schema(Config, base_schema=QuantitySchema)
    schema = Schema()

    # Default serialization (as float)
    result = schema.dump(config_obj)
    assert result["percentage_serialized_as_schema_default"] == 25.0

    # Override default serialization to string
    serialize_as_string_default.set(True)
    result = schema.dump(config_obj)
    assert result["percentage_serialized_as_schema_default"] == "25.0 %"
    serialize_as_string_default.set(False) # Reset context

    # Per-field configuration always takes precedence
    assert result["percentage_always_as_string"] == "25.0 %"
    assert result["percentage_always_as_float"] == 25.0
    ```
    """

    TYPE_MAPPING: dict[type, type[Field[Any]]] = QUANTITY_FIELD_CLASSES
