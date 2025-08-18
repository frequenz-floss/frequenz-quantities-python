# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Utils for testing the quantities with."""

import inspect
from collections.abc import Callable

from frequenz import quantities
from frequenz.quantities import Quantity
from frequenz.quantities._quantity import BaseValueT


class Fz1(
    Quantity[BaseValueT],
    exponent_unit_map={
        0: "Hz",
        3: "kHz",
    },
):
    """Frequency quantity with narrow exponent unit map."""


class Fz2(
    Quantity[BaseValueT],
    exponent_unit_map={
        -6: "uHz",
        -3: "mHz",
        0: "Hz",
        3: "kHz",
        6: "MHz",
        9: "GHz",
    },
):
    """Frequency quantity with broad exponent unit map."""


_CtorType = Callable[[BaseValueT], Quantity[BaseValueT]]

# This is the current number of subclasses. This probably will get outdated, but it will
# provide at least some safety against something going really wrong and end up testing
# an empty list. With this we should at least make sure we are not testing less classes
# than before. We don't get the actual number using len(_QUANTITY_SUBCLASSES) because it
# would defeat the purpose of the test.
_SANITFY_NUM_CLASSES = 7

_QUANTITY_SUBCLASSES = [
    cls
    for _, cls in inspect.getmembers(
        quantities,
        lambda m: inspect.isclass(m) and issubclass(m, Quantity) and m is not Quantity,
    )
]

# A very basic sanity check that are messing up the introspection
assert len(_QUANTITY_SUBCLASSES) >= _SANITFY_NUM_CLASSES

_QUANTITY_BASE_UNIT_STRINGS = [
    cls._new(0).base_unit  # pylint: disable=protected-access
    for cls in _QUANTITY_SUBCLASSES
]
for unit in _QUANTITY_BASE_UNIT_STRINGS:
    assert unit is not None

_QUANTITY_CTORS = [
    method
    for cls in _QUANTITY_SUBCLASSES
    for _, method in inspect.getmembers(
        cls,
        lambda m: inspect.ismethod(m)
        and m.__name__.startswith("from_")
        and m.__name__ != ("from_string"),
    )
]
# A very basic sanity check that are messing up the introspection. There are actually
# many more constructors than classes, but this still works as a very basic check.
assert len(_QUANTITY_CTORS) >= _SANITFY_NUM_CLASSES
