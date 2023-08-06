import os
from pathlib import Path
from rich import print


def copy_template(project_root: Path, fname: str):
    template_directory = Path(__file__).parent.joinpath("templates")
    with open(os.path.join(project_root, fname), "w") as f:
        with open(os.path.join(template_directory, fname), "r") as r:
            f.write(r.read())


def create_config_files(project_root: Path):
    # https://github.com/sdispater/tomlkit/blob/master/docs/quickstart.rst
    # TODO update quantready.toml with config params
    # launches a prompt to ask for configuration params and creates
    # .quantready # engine config file
    # .env # secrets and file added to gitignore if not already there
    # docker-compose.yml # launches all services

    for fname in ["quantready.toml", ".env", "docker-compose.yml"]:
        copy_template(project_root, fname)


def create_folder_structure(project_root: Path):
    for fdir in [
        "sources",  # api feeds as individual files
        "data/etl",  # data pipelines and feature store configs
        "data/features",
        "models",  # MLFlow root directory
        "libs",  # each folder is an internal library
        "envs",  # various environment configs
        "apis",  # each API as a sub-directory
        "services/reporting",
        "services/jupyterhub",
    ]:
        (project_root / fdir).mkdir(parents=True, exist_ok=True)


def initialize_project(project_root: str = "."):
    project_root = Path(project_root)
    project_root.mkdir(parents=True, exist_ok=True)
    if os.path.exists(os.path.join(project_root, "quantready.toml")):
        raise ValueError("Quantready is already initialized in this directory")

    print(
        ":runner: Initializing [bold green]Quantready[/bold green]"
        f"in directory: {project_root}"
    )
    create_config_files(project_root)
    create_folder_structure(project_root)

    if not os.path.exists(os.path.join(project_root, "quantready.toml")):
        raise RuntimeError("Quantready initialization failed in this directory")
