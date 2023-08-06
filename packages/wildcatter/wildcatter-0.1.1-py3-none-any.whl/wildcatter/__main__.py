"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Wildcatter."""


if __name__ == "__main__":
    main(prog_name="wildcatter")  # pragma: no cover
