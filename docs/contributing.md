# Contributing to CAP Alerts

Thank you for your interest in contributing to CAP Alerts!

## Development Setup

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/davidciani/cap-alerts.git
   cd cap-alerts
   ```

2. Install dependencies using uv:

   ```bash
   uv sync --group dev
   ```

3. Install prek hooks:

   ```bash
   prek install
   ```

## Making Changes

1. Create a new branch for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure tests pass:

   ```bash
   uv run pytest
   ```

3. Ensure code quality:

   ```bash
   uv run ruff check .
   uv run ruff format .
   uv run ty check
   ```

4. Commit your changes using [conventional commits](https://www.conventionalcommits.org/):

   ```bash
   git commit -m "feat: add new feature"
   ```

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/). Here are some examples:

- `feat: add new feature` - A new feature
- `fix: resolve bug in X` - A bug fix
- `docs: update README` - Documentation changes
- `refactor: simplify code` - Code refactoring
- `test: add tests for X` - Adding tests
- `chore: update dependencies` - Maintenance tasks

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Submit a pull request with a clear description
## Dependency Updates

This project uses Dependabot for automated dependency updates. Dependabot will automatically open pull requests when new versions are available for:

The `dependabot.yaml` at the root of this project is pre-configured to manage:

- GitHub Actions workflow dependencies
- Python dependencies (via `pyproject.toml`)
## Code Style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- We use [ty](https://docs.astral.sh/ty/) for type checking
- All code should be properly typed
- Write docstrings for public functions and classes