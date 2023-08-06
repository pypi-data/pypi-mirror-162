"""Console script for pyecodevices_rt2."""
import sys

import click


@click.command()
def main(args=None):
    """Console script for pyecodevices_rt2."""
    click.echo(
        "Replace this message by putting your code into " "pyecodevices_rt2.cli.main"
    )
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
