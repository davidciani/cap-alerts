# CAP Alerts

[![CI](https://github.com/davidciani/cap-alerts/actions/workflows/ci.yml/badge.svg)](https://github.com/davidciani/cap-alerts/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/cap_alerts.svg)](https://badge.fury.io/py/cap_alerts)
[![codecov](https://codecov.io/gh/davidciani/cap-alerts/branch/main/graph/badge.svg)](https://codecov.io/gh/davidciani/cap-alerts)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/type--checked-ty-blue?labelColor=orange)](https://github.com/astral-sh/ty)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/davidciani/cap-alerts/blob/main/LICENSE)

A Python package to consume, display, and analyze Common Alerting Protocol alerts.

## Features

- Fast and modern Python toolchain using Astral's tools (uv, ruff, ty)
- Type-safe with full type annotations
- Command-line interface built with Typer
- Comprehensive documentation with Zensical — [View Docs](https://davidciani.github.io/cap-alerts/)

## Installation

```bash
pip install cap_alerts
```

Or using uv (recommended):

```bash
uv add cap_alerts
```

## Quick Start

```python
import cap_alerts

print(cap_alerts.__version__)
```

### CLI Usage

```bash
# Show version
cap_alerts --version

# Say hello
cap_alerts hello World
```

## Development

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) for package management

### Setup

```bash
git clone https://github.com/davidciani/cap-alerts.git
cd cap-alerts
make install
```

### Running Tests

```bash
make test

# With coverage
make test-cov

# Across all Python versions
make test-matrix
```

### Code Quality

```bash
# Run all checks (lint, format, type-check)
make verify

# Auto-fix lint and format issues
make fix
```

### Prek

```bash
prek install
prek run --all-files
```

### Documentation

```bash
make docs-serve
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.