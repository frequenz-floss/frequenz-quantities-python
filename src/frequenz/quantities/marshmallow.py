# License: All rights reserved
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Custom marshmallow fields and schema."""

from typing import Any, Type

from marshmallow import Schema, ValidationError, fields

from ._current import Current
from ._energy import Energy
from ._frequency import Frequency
from ._percentage import Percentage
from ._power import Power
from ._quantity import Quantity
from ._temperature import Temperature
from ._voltage import Voltage


class _QuantityField(fields.Field):
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

    Instead, we dynamically create QuantityField subclasses for each Quantity
    that simply set the field_type attribute to the corresponding Quantity
    subclass.

    Those subclasses are generated and stored in the QUANTITY_FIELD_CLASSES
    mapping and are used for the TYPE_MAPPING in the `QuantitySchema`.
    """

    def __init__(self, field_type: Type[Quantity], **kwargs: Any) -> None:
        """
        Initialize the QuantityField.

        Args:
            field_type: The specific Quantity subclass (e.g., Percentage, Energy).
            **kwargs: Additional keyword arguments for the base Field.

        Raises:
            TypeError: If field_type is not a subclass of Quantity.
        """
        super().__init__(**kwargs)
        if not issubclass(field_type, Quantity):
            raise TypeError("field_type must be a subclass of Quantity.")
        self.field_type = field_type

    def _serialize(
        self, value: Quantity, attr: str | None, obj: Any, **kwargs: Any
    ) -> Any:
        """Serialize the Quantity object based on per-field configuration."""
        if not isinstance(value, self.field_type):
            raise ValidationError(f"Expected {self.field_type.__name__}.")

        assert self.parent is not None

        # Determine the serialization format
        serialize_as_string = self.metadata.get(
            "serialize_as_string",
            self.parent.context.get("serialize_as_string_default", False),
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
        if isinstance(value, str):
            # Use the Quantity's from_string method
            return self.field_type.from_string(value)
        if isinstance(value, (float, int)):
            # Use `_new` method for creating instance from base value
            return self.field_type._new(  # pylint: disable=protected-access
                float(value)
            )

        raise ValidationError("Invalid input type for QuantityField.")


_QUANTITY_SUBCLASSES = [
    Current,
    Energy,
    Frequency,
    Percentage,
    Power,
    Temperature,
    Voltage,
]


def _create_quantity_field_class(
    quantity_subclass: Type[Quantity],
) -> Type[fields.Field]:
    """Dynamically create a QuantityField subclass for a given Quantity subclass."""
    class_name = f"{quantity_subclass.__name__}Field"

    field_class: Type[fields.Field] = type(
        class_name,
        (_QuantityField,),
        {
            "__init__": lambda self, **kwargs: super(field_class, self).__init__(
                field_type=quantity_subclass, **kwargs
            ),
            "__module__": __name__,
        },
    )

    return field_class


QUANTITY_FIELD_CLASSES = {
    quantity_subclass: _create_quantity_field_class(quantity_subclass)
    for quantity_subclass in _QUANTITY_SUBCLASSES
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
    from frequenz.quantities import Percentage, QuantitySchema
    from typing import cast

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

        @classmethod
        def load(cls, config: dict[str, Any]) -> "Config":
            schema = class_schema(cls, base_schema=QuantitySchema)(
                serialize_as_string_default=True # type: ignore[call-arg]
            )
            return cast(Config, schema.load(config))
    ```
    """

    TYPE_MAPPING: dict[type[Quantity], type[fields.Field]] = QUANTITY_FIELD_CLASSES

    def __init__(
        self, *args: Any, serialize_as_string_default: bool = False, **kwargs: Any
    ) -> None:
        """
        Initialize the schema with a default serialization format.

        Args:
            *args: Additional positional arguments.
            serialize_as_string_default: Default serialization format for quantities.
                If True, quantities are serialized as strings with units.
                If False, quantities are serialized as floats.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.context["serialize_as_string_default"] = serialize_as_string_default
