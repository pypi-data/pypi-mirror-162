"""This CLI will evenutally be moved to gitpaid-cli-beta once the server is completed

The current package requirements are:
   `~/.poetry/bin/poetry add typer tabulate termcolor colorama`
"""
from pathlib import Path
from typing import List, Optional
import typer
from .initialize_project import initialize_project
import os
import subprocess
import sys
from rich import print

cli_app = typer.Typer()


@cli_app.command()
def init(dir: str = "."):
    """Initialize a new Quantready project"""
    try:
        initialize_project(dir)
    except ValueError as e:
        print(f":boom: [bold red]{e}[/bold red]")
        raise typer.Exit(1) from e


@cli_app.command()
def up(dir: str = ".", detach: bool = False):
    """Launch all services to run Quantready"""
    # detect file in directory
    # if file exists, run up

    compose_file = Path(dir).joinpath("docker-compose.yml")
    if not os.path.exists(compose_file):
        print(
            f":boom: [bold red]Quantready is not initialized in directory:[/bold red] {dir}"
        )
        raise typer.Exit(1)

    if detach:
        subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"])
    else:
        subprocess.run(["docker-compose", "-f", compose_file, "up"])


@cli_app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


# if __name__ == "__main__":
#     cli_app()
