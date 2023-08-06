import asyncio
import logging
import typer
from typing import List
from pathlib import Path
from gidgetlab.abc import GitLabAPI
from .models import GitLabId, Project
from . import api, producers

logger = logging.getLogger(__name__)


async def run_commit_file(
    gl: GitLabAPI,
    group: GitLabId,
    local_file_path: Path,
    repo_file_path: str,
    branch: str,
    commit_message: str,
    nb_consumers: int = 5,
) -> List[Project]:
    """Start producer and consumers to commit the file to all projects from group

    Return the list of projects
    """
    content = local_file_path.read_text()
    queue: asyncio.Queue[Project] = asyncio.Queue(maxsize=0)
    consumers = [
        asyncio.create_task(
            update_projects(queue, gl, repo_file_path, branch, content, commit_message)
        )
        for _ in range(nb_consumers)
    ]
    projects = await producers.produce_projects(gl, queue, group, archived=False)
    await queue.join()
    for consumer in consumers:
        consumer.cancel()
    await gl._client.aclose()
    return projects


async def update_projects(
    queue: asyncio.Queue,
    gl: GitLabAPI,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
) -> None:
    """Create or update the file in projects from the queue"""
    while True:
        project = await queue.get()
        typer.secho(
            f"Checking {project.path_with_namespace} (project id: {project.id})",
            fg=typer.colors.GREEN,
        )
        try:
            await api.commit_file_in_repository(
                gl,
                project.id,
                file_path,
                branch=branch,
                start_branch=branch,
                content=content,
                commit_message=commit_message,
            )
        except Exception as e:
            typer.secho(
                f"Updating {project.path_with_namespace} (project id: {project.id}) failed! {e}",
                fg=typer.colors.RED,
            )
        finally:
            queue.task_done()
