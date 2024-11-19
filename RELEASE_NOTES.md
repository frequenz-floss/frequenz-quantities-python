# Frequenz Quantities Library Release Notes

## Summary

This first stable release of `frequenz-quantities`!

The code is based on the quantities code in the [`frequenz-sdk` v1.0.0rc601](https://github.com/frequenz-floss/frequenz-sdk-python/releases/tag/v1.0.0-rc601) but with some new features and improvements.

## New Features

- Added support for `__round__` (`round(quantity)`), `__pos__` (`+quantity`) and `__mod__` (`quantity % quantity`) operators.
- Add `ReactivePower` quantity.
- Add `ApparentPower` quantity.
- Add an **experimental** marshmallow module available when adding `[marshmallow]` to the requirements. This module provides `marshmallow` fields for quantities and a `QuantitySchema` to use as a base schema that supports loading and dumping quantities.
