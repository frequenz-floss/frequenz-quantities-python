# Frequenz Quantities Library Release Notes

## Summary

This is the initial release, extracted from the [SDK v1.0.0rc601](https://github.com/frequenz-floss/frequenz-sdk-python/releases/tag/v1.0.0-rc601).

## New Features

- Added support for `__round__` (`round(quantity)`), `__pos__` (`+quantity`) and `__mod__` (`quantity % quantity`) operators.
- Add `ReactivePower` quantity.
- Add `ApparentPower` quantity.
- Add marshmallow module available when adding `[marshmallow]` to the requirements.
 - Add a QuantitySchema supporting string/float based serialization and deserialization of most quantities (except for `ReactivePower` and `ApparentPower`).
