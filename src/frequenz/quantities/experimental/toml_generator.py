# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Generate TOML configuration from marshmallow schemas.

This module walks marshmallow schemas (typically created via
`marshmallow_dataclass.class_schema`) and emits TOML text with default values
and field descriptions as comments.

The main entry point is
[`generate_toml_from_schema`][frequenz.quantities.experimental.toml_generator.generate_toml_from_schema],
which accepts a marshmallow schema and a TOML section name and returns the
rendered TOML string.

Danger:
    This module contains experimental features for which the API is not yet stable.

    Any module or class in this package may be removed or changed in a future release,
    even in minor or patch releases.

Example:
    ```python
    from dataclasses import dataclass, field
    from marshmallow_dataclass import class_schema
    from frequenz.quantities import Power
    from frequenz.quantities.experimental.marshmallow import QuantitySchema
    from frequenz.quantities.experimental.toml_generator import (
        generate_toml_from_schema,
    )

    @dataclass
    class MyConfig:
        threshold: float = field(
            default=0.5,
            metadata={"metadata": {"description": "Activation threshold."}},
        )
        name: str = field(
            default="default",
            metadata={"metadata": {"description": "Instance name."}},
        )
        max_power: Power = field(
            default_factory=lambda: Power.from_kilowatts(10.0),
            metadata={"metadata": {"description": "Maximum power output."}},
        )

    schema = class_schema(MyConfig, base_schema=QuantitySchema)()
    print(generate_toml_from_schema(schema, "my_config"))
    ```
"""

from __future__ import annotations

import enum
from datetime import timedelta
from typing import Any

import marshmallow

# Maximum line length used by the SHORT comment style to decide inline vs above.
_COMMENT_WRAP = 100


class CommentStyle(enum.Enum):
    """Controls where field descriptions are placed in the generated TOML.

    Members:
        AUTO: Inline when a usable default exists, above otherwise (default).
        ABOVE: Always place the comment on the line(s) above the key.
        INLINE: Always place the comment on the same line as the key.
        SHORT: Inline when the resulting line fits within the wrap limit,
               above otherwise.
    """

    AUTO = "auto"
    ABOVE = "above"
    INLINE = "inline"
    SHORT = "short"


def _resolve_nested(field: marshmallow.fields.Nested) -> marshmallow.Schema | None:
    """Resolve a Nested field to its schema instance, or None."""
    nested: Any = field.nested
    if callable(nested) and not isinstance(nested, type):
        try:
            nested = nested()
        except Exception:  # pylint: disable=broad-except
            return None
    if isinstance(nested, type):
        try:
            nested = nested()
        except Exception:  # pylint: disable=broad-except
            return None
    if isinstance(nested, marshmallow.Schema):
        return nested
    return None


def _resolve_default(default: Any) -> Any:
    """Resolve a default value, calling it if it's a callable."""
    if default is marshmallow.missing:
        return marshmallow.missing
    if callable(default) and not isinstance(default, type):
        try:
            return default()
        except Exception:  # pylint: disable=broad-except
            return marshmallow.missing
    return default


def _is_quantity_schema(schema: marshmallow.Schema | None) -> bool:
    """Check whether a schema wraps a Quantity type (Power, Percentage, etc.)."""
    if schema is None or schema.fields:
        return False
    try:
        from .marshmallow import (  # pylint: disable=import-outside-toplevel
            QUANTITY_FIELD_CLASSES,
        )

        return type(schema).__name__ in {k.__name__ for k in QUANTITY_FIELD_CLASSES}
    except ImportError:
        return False


def _has_usable_default(default: Any) -> bool:
    """Return True if *default* is a concrete value we can emit."""
    if default is None or default is marshmallow.missing:
        return False
    if isinstance(default, type):
        return False
    if isinstance(default, float) and (
        default == float("inf") or default == float("-inf")
    ):
        return False
    return True


def _format_value(value: Any, *, by_value: bool = True) -> str:
    """Format a Python value as a TOML literal."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, timedelta):
        return str(int(value.total_seconds()))
    if isinstance(value, enum.Enum):
        return f'"{value.value if by_value else value.name}"'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        if not value:
            return "[]"
        items = ", ".join(_format_value(v) for v in value)
        return f"[{items}]"
    # Quantity objects — use their human-readable string.
    if hasattr(value, "base_value"):
        return f'"{value}"'
    return repr(value)


def _first_line(text: str) -> str:
    """Return the first line of *text*."""
    return text.split("\n", 1)[0].strip()


def _first_sentence(text: str) -> str:
    """Return the first sentence of *text* (up to the first '.', '!', or '?')."""
    for i, ch in enumerate(text):
        if ch in ".!?":
            return text[: i + 1].strip()
    return text.strip()


def _above_comment(desc: str, *, first_sentence_only: bool) -> str:
    """Format *desc* as a ``# …`` comment line to appear above a key."""
    text = _first_sentence(desc) if first_sentence_only else _first_line(desc)
    return f"# {text}" if text else ""


def _comment_out(text: str) -> str:
    """Prefix every non-empty, non-comment line with ``# ``."""
    out: list[str] = []
    for line in text.split("\n"):
        if line and not line.startswith("#"):
            out.append(f"# {line}")
        else:
            out.append(line)
    return "\n".join(out)


def _emit_leaf(  # pylint: disable=too-many-arguments
    key: str,
    field: marshmallow.fields.Field[Any],
    default: Any,
    desc: str,
    *,
    style: CommentStyle = CommentStyle.AUTO,
    first_sentence_only: bool = False,
) -> str:
    """Return one or two TOML lines for a leaf field.

    Returns a single line for inline styles, or a comment line followed by
    the key-value line when the comment is placed above.
    """
    by_value = (
        getattr(field, "by_value", True)
        if isinstance(field, marshmallow.fields.Enum)
        else True
    )
    has_default = _has_usable_default(default)
    value_str = _format_value(default, by_value=by_value) if has_default else None

    # Build the key=value part (without any comment).
    if has_default:
        kv = f"{key} = {value_str}"
    else:
        kv = f"# {key} ="

    if not desc:
        return kv

    inline_comment = f"  # {_first_line(desc)}"
    above_comment = _above_comment(desc, first_sentence_only=first_sentence_only)

    def _with_inline() -> str:
        return f"{kv}{inline_comment}"

    def _with_above() -> str:
        if above_comment:
            return f"{above_comment}\n{kv}"
        return kv

    if style == CommentStyle.INLINE:
        return _with_inline()
    if style == CommentStyle.ABOVE:
        return _with_above()
    if style == CommentStyle.AUTO:
        # Inline when we have a default, above when we don't.
        return _with_inline() if has_default else _with_above()
    # SHORT: inline if the full line fits within the wrap limit, above otherwise.
    inline_line = _with_inline()
    if len(inline_line) <= _COMMENT_WRAP:
        return inline_line
    return _with_above()


# Each entry is (section_path, content_lines_str).
_Section = tuple[str, str]


def _collect_sections(
    schema: marshmallow.Schema,
    section_path: str,
    *,
    style: CommentStyle = CommentStyle.AUTO,
    first_sentence_only: bool = False,
) -> list[_Section]:
    """Walk a schema and return ``(section_path, body)`` pairs for TOML output."""
    sections: list[_Section] = []
    inline_lines: list[str] = []

    for name, field in schema.fields.items():
        key = field.data_key or name
        desc = field.metadata.get("description", "")
        default = _resolve_default(field.load_default)

        # --- Nested fields may become sub-sections or leaf values ---
        if isinstance(field, marshmallow.fields.Nested):
            nested_schema = _resolve_nested(field)

            if _is_quantity_schema(nested_schema):
                # Quantity → treat as a leaf value.
                inline_lines.append(
                    _emit_leaf(
                        key,
                        field,
                        default,
                        desc,
                        style=style,
                        first_sentence_only=first_sentence_only,
                    )
                )
            elif nested_schema is not None and nested_schema.fields:
                sub = _collect_sections(
                    nested_schema,
                    f"{section_path}.{key}",
                    style=style,
                    first_sentence_only=first_sentence_only,
                )
                if default is None:
                    # Optional section → comment everything out.
                    sections.extend((p, _comment_out(c)) for p, c in sub)
                else:
                    sections.extend(sub)
            else:
                # Unresolvable nested (e.g. forward-ref string) → leaf.
                inline_lines.append(
                    _emit_leaf(
                        key,
                        field,
                        default,
                        desc,
                        style=style,
                        first_sentence_only=first_sentence_only,
                    )
                )
            continue

        # --- All other field types are leaves ---
        inline_lines.append(
            _emit_leaf(
                key,
                field,
                default,
                desc,
                style=style,
                first_sentence_only=first_sentence_only,
            )
        )

    body = "\n".join(inline_lines)
    if body.strip():
        sections.insert(0, (section_path, body))
    elif not sections:
        sections.append((section_path, ""))

    return sections


def generate_toml_from_schema(
    schema: marshmallow.Schema,
    section: str,
    *,
    style: CommentStyle = CommentStyle.AUTO,
    first_sentence_only: bool = False,
) -> str:
    """Generate TOML text from a marshmallow schema.

    Walks the schema's fields recursively, emitting TOML sections with
    default values and field descriptions as comments.

    Nested dataclass fields become ``[section.subsection]`` headers.
    Quantity fields (Power, Percentage, etc.) are rendered as string
    leaf values.  Optional nested sections (where the default is ``None``)
    are emitted fully commented out.

    Args:
        schema: A marshmallow Schema instance to walk.
        section: The top-level TOML section name (e.g. ``"my_actor"``).
        style: Where to place field descriptions relative to the key.
        first_sentence_only: When placing comments above a key, truncate
            to the first sentence rather than the first line.

    Returns:
        The generated TOML text as a string (without trailing newline).
    """
    lines: list[str] = []
    for section_path, content in _collect_sections(
        schema, section, style=style, first_sentence_only=first_sentence_only
    ):
        lines.append(f"[{section_path}]")
        if content.strip():
            lines.append(content)
    return "\n".join(lines)
