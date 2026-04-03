# CAP Alerts

A Python package to consume, display, and analyze Common Alerting Protocol alerts.

## Installation

Install using pip:

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

### Command Line Interface

CAP Alerts provides a command-line interface:

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

Clone the repository and install dependencies:

```bash
git clone https://github.com/davidciani/cap-alerts.git
cd cap-alerts
uv sync --group dev
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run ty check
```

### Prek Hooks

Install prek hooks:

```bash
prek install
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/davidciani/cap-alerts/blob/main/LICENSE) file for details.