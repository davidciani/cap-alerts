
# List - list all commands
list:
    @just --list

# Verify - check everything without making changes
verify: lint-check format-check type-check

# Fix - automatically fix what can be fixed
fix: lint-fix format-fix

# Lint
lint-check:
    uv run ruff check .

# Fix lint issues
lint-fix:
    uv run ruff check . --fix
    uv run ruff check --select I --fix .

# Check formatting
format-check:
    uv run ruff format --check .

# Fix formatting
format-fix:
    uv run ruff format .

# Type check
type-check:
    uv run ty check .

# Run all tests
test:
    uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    uv run pytest --cov --cov-report=xml --cov-report=term-missing

# Run tests across all Python versions
test-matrix:
    uv run hatch test

# Run tests with coverage across all Python versions
test-matrix-cov:
    uv run hatch test --cover

# Install dependencies
install:
    uv sync --all-groups

# Build the project, useful for checking that packaging is correct
build:
    rm -rf build
    rm -rf dist
    uv build


# Serve documentation
docs-serve:
    -lsof -ti :8000 | xargs kill
    uv run --group docs zensical serve


# Build Documentation
docs-build:
    uv run --group docs zensical build --clean



# Secret scanning
secrets:
    gitleaks detect --redact 80

# Dependency audit
pysentry:
    uv run pysentry-rs




# Remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test

# Remove build artifacts
clean-build:
    rm -fr build/
    rm -fr dist/
    rm -fr .eggs/
    find . -name '*.egg-info' -exec rm -fr {} +
    find . -name '*.egg' -exec rm -f {} +

# Remove Python file artifacts
clean-pyc:
    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f {} +
    find . -name '__pycache__' -exec rm -fr {} +

# Remove test and coverage artifacts
clean-test:
    rm -f .coverage
    rm -f .coverage.*
    rm -fr htmlcov/
    rm -fr .pytest_cache