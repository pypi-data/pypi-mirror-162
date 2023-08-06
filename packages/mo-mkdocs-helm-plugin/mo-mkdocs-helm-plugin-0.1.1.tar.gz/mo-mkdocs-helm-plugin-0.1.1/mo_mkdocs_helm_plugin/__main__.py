# type: ignore[attr-defined]
from typing import Optional

from enum import Enum
from random import choice

import typer
from rich.console import Console

from mo_mkdocs_helm_plugin import version
from mo_mkdocs_helm_plugin.repository import HelmRepositoryPlugin


class Color(str, Enum):
    white = "white"
    red = "red"
    cyan = "cyan"
    magenta = "magenta"
    yellow = "yellow"
    green = "green"


app = typer.Typer(
    name="mo-mkdocs-helm-plugin",
    help="A mkdocs plugin to enable serving a helm chart via a github page",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]mo-mkdocs-helm-plugin[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.command()
def main(
    color: Optional[Color] = typer.Option(
        None,
        "-c",
        "--color",
        "--colour",
        case_sensitive=False,
        help="Color for print. If not specified then choice will be random.",
    ),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the mo-mkdocs-helm-plugin package.",
    ),
) -> None:
    """Print a greeting with a giving name."""
    if color is None:
        color = choice(list(Color))

    console.print(f"[bold {color}]{HelmRepositoryPlugin()}[/]")


if __name__ == "__main__":
    app()
