import asyncio
import shutil
import typer
from typing import List
from pathlib import Path
from gidgetlab.abc import GitLabAPI
from .models import GitLabId, Project
from .util import run_subprocess
from . import producers


async def run_clone(
    gl: GitLabAPI,
    group: GitLabId,
    path: Path,
    archived: bool = False,
    delete_extra_repos: bool = False,
    force: bool = False,
    nb_consumers: int = 5,
) -> List[Project]:
    """Start producer and consumers to clone all projects from group

    Return the list of projects
    """
    queue: asyncio.Queue[Project] = asyncio.Queue(maxsize=0)
    consumers = [
        asyncio.create_task(clone_projects(queue, path, force))
        for _ in range(nb_consumers)
    ]
    projects = await producers.produce_projects(gl, queue, group, archived)
    await queue.join()
    for consumer in consumers:
        consumer.cancel()
    await gl._client.aclose()
    if delete_extra_repos:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, delete_extra_repositories, projects, path)
    return projects


def delete_extra_repositories(projects: List[Project], path: Path) -> List[Path]:
    """Delete local git repositories not part of the list of projects

    WARNING! All projects are expected to be part of the same base namespace

    Return the list of deleted path
    """
    if not projects:
        return []
    root = path / projects[0].base_namespace
    cloned_repos = {path / project.path_with_namespace for project in projects}
    local_repos = {git_folder.parent for git_folder in root.glob("**/.git")}
    extra_repos = local_repos - cloned_repos
    for repo in extra_repos:
        typer.secho(f"Delete {repo}", fg=typer.colors.RED)
        shutil.rmtree(repo)
    return sorted(list(extra_repos))


async def clone_project(project: Project, path: Path, force: bool = False) -> None:
    """Clone or update project"""
    project_path = path / project.path_with_namespace
    if project_path.exists():
        if project.default_branch is None:
            # Git repo is empty
            typer.secho(f"Skip empty project {project.name}", fg=typer.colors.GREEN)
            return
        typer.secho(
            f"Update {project.name} under {project_path}", fg=typer.colors.GREEN
        )
        if force:
            await run_subprocess("git fetch", cwd=project_path)
            await run_subprocess(
                f"git reset --hard origin/{project.default_branch}",
                cwd=project_path,
            )
        else:
            await run_subprocess("git pull --rebase", cwd=project_path)
    else:
        parent = project_path.parent
        if not parent.exists():
            typer.secho(f"Create {parent} directory", fg=typer.colors.GREEN)
            parent.mkdir(parents=True, exist_ok=True)
        typer.secho(f"Clone {project.name} under {project_path}", fg=typer.colors.GREEN)
        await run_subprocess(f"git clone {project.ssh_url} {project_path}")


async def clone_projects(queue: asyncio.Queue, path: Path, force: bool = False) -> None:
    """Clone or update projects from queue"""
    while True:
        project = await queue.get()
        try:
            await clone_project(project, path, force)
        except Exception as e:
            typer.secho(
                f"Cloning {project.path_with_namespace} (project id: {project.id}) failed! {e}",
                fg=typer.colors.RED,
            )
        finally:
            queue.task_done()
