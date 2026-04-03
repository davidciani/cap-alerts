"""Command-line interface for cap_alerts."""

import typer

from cap_alerts import __version__

app = typer.Typer(
    name="cap_alerts",
    help="A Python package to consume, display, and analyze Common Alerting Protocol alerts.",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"cap_alerts version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """A Python package to consume, display, and analyze Common Alerting Protocol alerts."""


@app.command()
def hello(
    name: str = typer.Argument("World", help="Name to greet"),
) -> None:
    """Say hello to someone."""
    typer.echo(f"Hello, {name}!")


if __name__ == "__main__":
    app()
