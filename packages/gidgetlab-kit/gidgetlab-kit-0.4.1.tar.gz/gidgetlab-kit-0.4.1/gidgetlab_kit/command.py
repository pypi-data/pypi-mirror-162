import asyncio
import logging
import typer
import httpx
from importlib.metadata import version, PackageNotFoundError  # type: ignore
from pathlib import Path
from typing import Optional, List
from gidgetlab.httpx import GitLabAPI
from . import util, api
from .models import GitLabId
from .clone import run_clone
from .get import run_get
from .pipelines import run_trigger_group_pipelines
from .commits import run_commit_file

try:
    __version__ = version("gidgetlab-kit")
except PackageNotFoundError:
    __version__ = "unknown"

app = typer.Typer()
state = {"gl": None}


def version_callback(value: bool):
    if value:
        typer.echo(f"gidgetlab-kit version: {__version__}")
        raise typer.Exit()


async def run_list_projects(gl: GitLabAPI, group_id: GitLabId, archived: bool) -> None:
    typer.echo(f"Projects under group {group_id}:")
    async for project in api.get_all_projects(gl, group_id, archived):
        typer.secho(
            f"{project.path_with_namespace} (id: {project.id} name: {project.name})",
            fg=typer.colors.GREEN,
        )
    await gl._client.aclose()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the current version and exit.",
    ),
    url: str = typer.Option("https://gitlab.com", envvar="GL_URL", help="GitLab URL"),
    access_token: str = typer.Option(
        "", envvar="GL_ACCESS_TOKEN", help="GitLab access token"
    ),
    verify: bool = typer.Option(
        True, help="Verify SSL cerificate or disable verification"
    ),
):
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    client = httpx.AsyncClient(verify=verify)
    state["gl"] = GitLabAPI(client, "gidgetlab", url=url, access_token=access_token)


@app.command()
def clone(
    group: str = typer.Argument(..., help="Name of the group to clone"),
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        exists=True,
        resolve_path=True,
        help="Path where to clone the group",
    ),
    archived: bool = typer.Option(False, help="Clone archived projects"),
    delete_extra_repos: bool = typer.Option(
        False, help="Delete extra local repositories"
    ),
    force: bool = typer.Option(
        False,
        help="Force repository update when it exists (git reset --hard origin/default_branch instead of rebase)",
    ),
    nb_consumers: int = typer.Option(
        5,
        "--nb-consumers",
        "-n",
        help="Number of consumers to start to clone in parallel",
    ),
):
    """Clone or pull all projects from group (including subgroups)

    Projects are cloned/updated in parallel
    """
    asyncio.run(
        run_clone(
            state["gl"], group, path, archived, delete_extra_repos, force, nb_consumers
        )
    )


@app.command()
def get(
    endpoint: str = typer.Argument(..., help="Endpoint to get"),
    parameters: List[str] = typer.Argument(
        None, help="Optional key-value pairs to pass as json parameters"
    ),
    nb_items: int = typer.Option(
        0,
        "--nb-items",
        "-n",
        help="Number of items to retrieve. Only valid when a list is returned. Set to 0 to return all.",
    ),
):
    """Get one or several items from the given endpoint"""
    try:
        params = util.convert_params_to_dict(parameters)
    except ValueError:
        typer.echo(
            f"Invalid parameters: '{' '.join(parameters)}' should be a list of key-value pairs separated by '='."
        )
        raise typer.Exit(code=1)
    asyncio.run(run_get(state["gl"], endpoint, params, nb_items))


@app.command()
def list_projects(
    group: str = typer.Argument(..., help="Name of the group"),
    archived: bool = typer.Option(False, help="List archived projects"),
):
    """List all projects from group (including subgroups)"""
    asyncio.run(run_list_projects(state["gl"], group, archived))


@app.command()
def trigger_pipelines(
    group: str = typer.Argument(..., help="Name of the group"),
    nb_projects: int = typer.Option(
        0,
        "--nb-projects",
        "-n",
        help="Number of projects to trigger. Set to 0 to trigger all projects from the group.",
    ),
    random: bool = typer.Option(
        False,
        help="Randomly pick the projects. Select the oldest that were triggered otherwise.",
    ),
    exclude: List[str] = typer.Option(
        [],
        help="Project to exclude (path with basename)",
    ),
    description: str = typer.Option(
        "gidgetlab",
        help="Pipeline trigger description",
    ),
):
    """Trigger the pipeline for all or a subset of projects from group"""
    asyncio.run(
        run_trigger_group_pipelines(
            state["gl"], group, nb_projects, random, description, exclude
        )
    )


@app.command()
def commit_file(
    filepath: Path = typer.Argument(..., help="Local file to add or update"),
    group: str = typer.Option(..., help="Name of the group"),
    repo_path: Path = typer.Option(
        Path("."),
        "--repo-path",
        "-p",
        resolve_path=False,
        help="Path of the file in the repository",
    ),
    message: str = typer.Option(
        "",
        "--message",
        "-m",
        show_default=False,
        help="Commit message [default: Add/Update <filename>]",
    ),
    branch: str = typer.Option("master", "--branch", "-b", help="Branch to commit to"),
    nb_consumers: int = typer.Option(
        5,
        "--nb-consumers",
        "-n",
        help="Number of consumers to start to update in parallel",
    ),
):
    """Add or update a file to a list of projects

    Example:

      The following will add the local .gitlab-ci.yml file to all projects under the my-group group

      $ gidgetlab commit-file --group my-group .gitlab-ci.yml
    """
    repo_file_path = str(repo_path / filepath.name)
    asyncio.run(
        run_commit_file(
            state["gl"],
            group,
            filepath,
            repo_file_path,
            branch,
            message,
            nb_consumers,
        )
    )
