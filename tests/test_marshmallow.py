# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Test marshmallow fields and schema."""


from dataclasses import dataclass, field
from typing import Any, Self, cast

from marshmallow_dataclass import class_schema

from frequenz.quantities import Energy, Percentage, Power, Temperature, Voltage
from frequenz.quantities.marshmallow import QuantitySchema


@dataclass
class Config:
    """Configuration test class."""

    my_percent_field: Percentage = field(
        default_factory=lambda: Percentage.from_percent(25.0),
        metadata={
            "metadata": {
                "description": "A percentage field",
            },
        },
    )

    my_power_field: Power = field(
        default_factory=lambda: Power.from_watts(100.0),
        metadata={
            "metadata": {
                "description": "A power field",
            },
        },
    )

    my_energy_field: Energy = field(
        default_factory=lambda: Energy.from_watt_hours(100.0),
        metadata={
            "metadata": {
                "description": "An energy field",
            },
        },
    )

    voltage_always_string: Voltage = field(
        default_factory=lambda: Voltage.from_kilovolts(200.0),
        metadata={
            "metadata": {
                "description": "A voltage field that is always serialized as a string",
                "serialize_as_string": True,
            },
        },
    )

    temp_never_string: Temperature = field(
        default_factory=lambda: Temperature.from_celsius(100.0),
        metadata={
            "metadata": {
                "description": "A temperature field that is never serialized as a string",
                "serialize_as_string": False,
            },
        },
    )

    @classmethod
    def load(cls, config: dict[str, Any]) -> Self:
        """Load the configuration."""
        schema = class_schema(cls, base_schema=QuantitySchema)()
        return cast(Self, schema.load(config))

    def dump(self, serialize_as_string_default: bool = False) -> dict[str, Any]:
        """Dump the configuration."""
        schema = class_schema(Config, base_schema=QuantitySchema)(
            serialize_as_string_default=serialize_as_string_default  # type: ignore[call-arg]
        )
        return cast(dict[str, Any], schema.dump(self))


def test_config_schema_load() -> None:
    """Test that the values are correctly loaded."""
    config = Config.load(
        {
            "my_percent_field": 50.0,
            "my_power_field": 200.0,
            "my_energy_field": 200.0,
            "voltage_always_string": 250_000.0,
            "temp_never_string": 100.0,
        }
    )

    assert config.my_percent_field == Percentage.from_percent(50.0)
    assert config.my_power_field == Power.from_watts(200.0)
    assert config.my_energy_field == Energy.from_watt_hours(200.0)
    assert config.voltage_always_string == Voltage.from_kilovolts(250.0)
    assert config.temp_never_string == Temperature.from_celsius(100.0)


def test_config_schema_load_defaults() -> None:
    """Test that the defaults are correctly loaded."""
    config = Config.load({})

    assert config.my_percent_field == Percentage.from_percent(25.0)
    assert config.my_power_field == Power.from_watts(100.0)
    assert config.my_energy_field == Energy.from_watt_hours(100.0)
    assert config.voltage_always_string == Voltage.from_kilovolts(200)
    assert config.temp_never_string == Temperature.from_celsius(100.0)


def test_config_schema_load_from_string() -> None:
    """Test that the values are correctly loaded from string."""
    config = Config.load(
        {
            "my_percent_field": "50 %",
            "my_power_field": "200 W",
            "my_energy_field": "200 Wh",
            "voltage_always_string": "250 kV",
            "temp_never_string": "10 °C",
        }
    )

    assert config.my_percent_field == Percentage.from_percent(50.0)
    assert config.my_power_field == Power.from_watts(200.0)
    assert config.my_energy_field == Energy.from_watt_hours(200.0)
    assert config.voltage_always_string == Voltage.from_kilovolts(250.0)
    assert config.temp_never_string == Temperature.from_celsius(10.0)


def test_config_schema_load_from_mixed() -> None:
    """Test that the values are correctly loaded from mixed."""
    config = Config.load(
        {
            "my_percent_field": "50 %",
            "my_power_field": 200,
            "my_energy_field": "200 Wh",
            "voltage_always_string": 250_000,
            "temp_never_string": "10 °C",
        }
    )

    assert config.my_percent_field == Percentage.from_percent(50.0)
    assert config.my_power_field == Power.from_watts(200.0)
    assert config.my_energy_field == Energy.from_watt_hours(200.0)
    assert config.voltage_always_string == Voltage.from_kilovolts(250.0)
    assert config.temp_never_string == Temperature.from_celsius(10.0)


def test_config_schema_dump_default_float() -> None:
    """Test that the values are correctly dumped."""
    config = Config(
        my_percent_field=Percentage.from_percent(50.0),
        my_power_field=Power.from_watts(200.0),
        my_energy_field=Energy.from_watt_hours(200.0),
        voltage_always_string=Voltage.from_kilovolts(250.0),
        temp_never_string=Temperature.from_celsius(10.0),
    )

    dumped = config.dump(serialize_as_string_default=False)

    assert dumped == {
        "my_percent_field": 50.0,
        "my_power_field": 200.0,
        "my_energy_field": 200.0,
        "voltage_always_string": "250 kV",
        "temp_never_string": 10.0,
    }


def test_config_schema_dump_default_string() -> None:
    """Test that the values are correctly dumped."""
    config = Config(
        my_percent_field=Percentage.from_percent(50.0),
        my_power_field=Power.from_watts(200.0),
        my_energy_field=Energy.from_watt_hours(200.0),
        voltage_always_string=Voltage.from_kilovolts(250.0),
        temp_never_string=Temperature.from_celsius(10.0),
    )

    dumped = config.dump(serialize_as_string_default=True)

    assert dumped == {
        "my_percent_field": "50 %",
        "my_power_field": "200 W",
        "my_energy_field": "200 Wh",
        "voltage_always_string": "250 kV",
        "temp_never_string": 10.0,
    }
