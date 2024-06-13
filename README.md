# Frequenz Quantities Library

[![Build Status](https://github.com/frequenz-floss/frequenz-quantities-python/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-quantities-python/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-quantities)](https://pypi.org/project/frequenz-quantities/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-quantities-python/)

## Introduction

This library provide types for holding quantities with units. The main goal is
to avoid mistakes while working with different types of quantities, for example
avoiding adding a length to a time.

It also prevents mistakes when operating between the same quantity but in
different units, like adding a power in Joules to a power in Watts without
converting one of them.

Quantities store the value in a base unit, and then provide methods to get that
quantity as a particular unit.

## Documentation

For more information on how to use this library and examples, please check the
[Documentation website](https://frequenz-floss.github.io/frequenz-quantities-python/).

## Supported Platforms

The following platforms are officially supported (tested):

- **Python:** 3.11
- **Operating System:** Ubuntu Linux 20.04
- **Architectures:** amd64, arm64

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
