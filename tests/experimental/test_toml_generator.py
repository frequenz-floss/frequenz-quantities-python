# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test TOML config generation from marshmallow schemas."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

from marshmallow_dataclass import class_schema

from frequenz.quantities import Percentage, Power
from frequenz.quantities.experimental.marshmallow import QuantitySchema
from frequenz.quantities.experimental.toml_generator import (
    CommentStyle,
    generate_toml_from_schema,
)

# ---- Test dataclasses ----


@dataclass
class SimpleConfig:
    """A simple config with basic leaf fields."""

    name: str = field(
        default="hello",
        metadata={"metadata": {"description": "The instance name."}},
    )
    count: int = field(
        default=42,
        metadata={"metadata": {"description": "Number of retries."}},
    )
    enabled: bool = field(
        default=True,
        metadata={"metadata": {"description": "Whether the feature is enabled."}},
    )
    ratio: float = field(
        default=0.75,
        metadata={"metadata": {"description": "Ratio value."}},
    )


@dataclass
class NoDefaultConfig:
    """Config with a field that has no default."""

    required_field: str = field(
        metadata={"metadata": {"description": "This field is required."}},
    )


@dataclass
class NestedChild:
    """A child config section."""

    timeout: int = field(
        default=30,
        metadata={"metadata": {"description": "Timeout in seconds."}},
    )
    verbose: bool = field(
        default=False,
        metadata={"metadata": {"description": "Enable verbose logging."}},
    )


@dataclass
class NestedParent:
    """A parent config with a nested section."""

    label: str = field(
        default="main",
        metadata={"metadata": {"description": "The label."}},
    )
    child: NestedChild = field(default_factory=NestedChild)


@dataclass
class OptionalNestedParent:
    """A parent config with an optional nested section."""

    label: str = field(
        default="main",
        metadata={"metadata": {"description": "The label."}},
    )
    child: Optional[NestedChild] = field(  # noqa: UP007
        default=None,
    )


class Color(enum.Enum):
    """A color enum."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclass
class EnumConfig:
    """Config with an enum field."""

    color: Color = field(
        default=Color.GREEN,
        metadata={"metadata": {"description": "The primary color."}},
    )


@dataclass
class TimedeltaConfig:
    """Config with a timedelta field."""

    interval: timedelta = field(
        default_factory=lambda: timedelta(seconds=60),
        metadata={"metadata": {"description": "Polling interval."}},
    )


@dataclass
class ListConfig:
    """Config with a list field."""

    tags: list[str] = field(
        default_factory=list,
        metadata={"metadata": {"description": "A list of tags."}},
    )


@dataclass
class NoDescConfig:
    """Config with a field that has no description."""

    value: int = field(default=10)


@dataclass
class QuantityConfig:
    """Config with quantity fields."""

    max_power: Power = field(
        default_factory=lambda: Power.from_kilowatts(10.0),
        metadata={"metadata": {"description": "Maximum power output."}},
    )
    threshold: Percentage = field(
        default_factory=lambda: Percentage.from_percent(80.0),
        metadata={"metadata": {"description": "Activation threshold."}},
    )
    label: str = field(
        default="test",
        metadata={"metadata": {"description": "A label."}},
    )


@dataclass
class InfDefaultConfig:
    """Config with infinity defaults (should be treated as no-default)."""

    upper: float = field(
        default=float("inf"),
        metadata={"metadata": {"description": "Upper bound."}},
    )
    lower: float = field(
        default=float("-inf"),
        metadata={"metadata": {"description": "Lower bound."}},
    )


# ---- Tests ----


def test_simple_leaf_fields() -> None:
    """Test generation of simple leaf fields with defaults and descriptions."""
    schema = class_schema(SimpleConfig)()
    result = generate_toml_from_schema(schema, "simple")

    assert "[simple]" in result
    assert 'name = "hello"  # The instance name.' in result
    assert "count = 42  # Number of retries." in result
    assert "enabled = true  # Whether the feature is enabled." in result
    assert "ratio = 0.75  # Ratio value." in result


def test_no_default_field() -> None:
    """Test that fields without defaults are commented out."""
    schema = class_schema(NoDefaultConfig)()
    result = generate_toml_from_schema(schema, "section")

    assert "# This field is required." in result
    assert "# required_field =" in result


def test_nested_section() -> None:
    """Test that nested dataclasses become sub-sections."""
    schema = class_schema(NestedParent)()
    result = generate_toml_from_schema(schema, "parent")

    assert "[parent]" in result
    assert 'label = "main"' in result
    assert "[parent.child]" in result
    assert "timeout = 30" in result
    assert "verbose = false" in result


def test_optional_nested_commented_out() -> None:
    """Test that optional nested sections (default=None) are fully commented out."""
    schema = class_schema(OptionalNestedParent)()
    result = generate_toml_from_schema(schema, "parent")

    assert "[parent]" in result
    assert 'label = "main"' in result
    # The child section header should still be present but the body commented out
    assert "[parent.child]" in result
    assert "# timeout = 30" in result
    assert "# verbose = false" in result


def test_enum_field() -> None:
    """Test enum fields render as a quoted string."""
    schema = class_schema(EnumConfig)()
    result = generate_toml_from_schema(schema, "cfg")

    # marshmallow serializes enums by name by default
    assert 'color = "GREEN"' in result


def test_timedelta_field() -> None:
    """Test timedelta fields render as integer seconds."""
    schema = class_schema(TimedeltaConfig)()
    result = generate_toml_from_schema(schema, "cfg")

    assert "interval = 60" in result


def test_empty_list_field() -> None:
    """Test that empty list defaults are treated as no-default (commented out)."""
    schema = class_schema(ListConfig)()
    result = generate_toml_from_schema(schema, "cfg")

    # Empty list is falsy → _has_usable_default returns False → commented out
    assert "# tags =" in result


def test_no_description() -> None:
    """Test fields without descriptions produce no comment."""
    schema = class_schema(NoDescConfig)()
    result = generate_toml_from_schema(schema, "cfg")

    assert "value = 10" in result
    assert "#" not in result.split("value = 10")[1].split("\n")[0]


def test_comment_style_above() -> None:
    """Test ABOVE comment style always puts comments above."""
    schema = class_schema(SimpleConfig)()
    result = generate_toml_from_schema(schema, "s", style=CommentStyle.ABOVE)

    lines = result.split("\n")
    # Find the "name" key line
    for i, line in enumerate(lines):
        if line.startswith('name = "hello"'):
            assert lines[i - 1] == "# The instance name."
            # No inline comment
            assert "#" not in line
            break
    else:
        raise AssertionError("name key not found")


def test_comment_style_inline() -> None:
    """Test INLINE comment style always puts comments inline."""
    schema = class_schema(NoDefaultConfig)()
    result = generate_toml_from_schema(schema, "s", style=CommentStyle.INLINE)

    # Even fields without defaults get inline comments
    assert "# required_field =  # This field is required." in result


def test_comment_style_short() -> None:
    """Test SHORT comment style uses inline when line fits."""
    schema = class_schema(SimpleConfig)()
    result = generate_toml_from_schema(schema, "s", style=CommentStyle.SHORT)

    # Short enough → inline
    assert 'name = "hello"  # The instance name.' in result


def test_quantity_fields_as_leaves() -> None:
    """Test that Quantity fields are rendered as leaf string values."""
    schema = class_schema(QuantityConfig, base_schema=QuantitySchema)()
    result = generate_toml_from_schema(schema, "actor")

    assert "[actor]" in result
    # Quantities should be rendered as string leaves, not sub-sections
    assert "max_power" in result
    assert "threshold" in result
    assert 'label = "test"' in result
    # Should NOT have [actor.max_power] as a sub-section
    assert "[actor.max_power]" not in result
    assert "[actor.threshold]" not in result


def test_infinity_defaults_treated_as_no_default() -> None:
    """Test that +/-inf defaults are treated as no-default (commented out)."""
    schema = class_schema(InfDefaultConfig)()
    result = generate_toml_from_schema(schema, "cfg")

    assert "# upper =" in result
    assert "# lower =" in result


def test_first_sentence_only() -> None:
    """Test first_sentence_only truncation of descriptions."""

    @dataclass
    class LongDescConfig:
        """Config with a long multi-sentence description."""

        value: int = field(
            default=5,
            metadata={
                "metadata": {
                    "description": "The main value. Used for calculations. Do not change."
                }
            },
        )

    schema = class_schema(LongDescConfig)()

    # Without first_sentence_only — should show full first line
    result_full = generate_toml_from_schema(schema, "cfg")
    assert "The main value. Used for calculations. Do not change." in result_full

    # With first_sentence_only on ABOVE style — should truncate
    result_short = generate_toml_from_schema(
        schema, "cfg", style=CommentStyle.ABOVE, first_sentence_only=True
    )
    assert "# The main value." in result_short
    assert "Used for calculations" not in result_short


def test_multiple_sections_output_format() -> None:
    """Test that the overall output format has proper section headers."""
    schema = class_schema(NestedParent)()
    result = generate_toml_from_schema(schema, "my_actor")

    lines = result.split("\n")
    # First non-empty line should be the section header
    assert lines[0] == "[my_actor]"
    # Should contain the child section somewhere
    assert any(line == "[my_actor.child]" for line in lines)


def test_empty_schema() -> None:
    """Test that an empty schema produces a section header with empty body."""

    @dataclass
    class EmptyConfig:
        """Config with no fields."""

    schema = class_schema(EmptyConfig)()
    result = generate_toml_from_schema(schema, "empty")

    assert "[empty]" in result
