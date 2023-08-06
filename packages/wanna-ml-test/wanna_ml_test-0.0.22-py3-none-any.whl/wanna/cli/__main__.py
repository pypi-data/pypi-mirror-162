import typer

app = typer.Typer()

import json

import pkg_resources
import requests

PYPI_URL = "https://pypi.org/pypi/wanna-ml/json"
UPDATE_MESSAGE = (
    "If you used `pipx` to install WANNA CLI, use the following command:\n\n"
    "pipx upgrade wanna\n\n"
    f"Otherwise, use `pip install --upgrade {__package__}`"
    "(exact command will depend on your environment).\n\n"
)


def get_latest_version() -> str:
    try:
        resp = requests.get(PYPI_URL)
        resp.raise_for_status()
    except (ConnectionError, requests.exceptions.RequestException):
        typer.echo("Failed to retrieve versions")
        return ""
    data = json.loads(resp.text)
    return data["info"]["version"]


def perform_check() -> None:
    """Perform the version check and instructs the user about the next steps"""

    latest_version = get_latest_version()
    version = pkg_resources.get_distribution("wanna-ml-test").version
    if latest_version and version < latest_version:
        typer.echo(
            f"Installed version is {version}, the latest version is {latest_version}",
        )
        typer.echo(
            UPDATE_MESSAGE,
        )
    else:
        typer.echo(f"Your wanna cli is up to date with {latest_version}")


@app.callback()
def callback():
    """
    Awesome Portal Gun
    """


@app.command()
def version():
    """
    Shoot the portal gun
    """
    perform_check()


@app.command()
def load():
    """
    Load the portal gun
    """
    typer.echo("Loading portal gun")
