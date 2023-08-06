import asyncio
import httpx
import logging
from typing import Optional, Callable, Awaitable, List, Any
from gidgetlab.httpx import GitLabAPI
from .models import Project, GitLabId
from .api import get_projects, get_all_projects

logger = logging.getLogger(__name__)


async def run_on_project(
    gl: GitLabAPI,
    queue: asyncio.Queue,
    func: Callable[[GitLabAPI, Project, Any], Awaitable[Any]],
    *args,
    **kwargs,
) -> None:
    """Run on projects from queue"""
    while True:
        project = await queue.get()
        try:
            await func(gl, project, *args, **kwargs)
        except Exception as e:
            logger.warning(
                f"Running {func} on {project.path_with_namespace} (project id: {project.id}) failed! {e}",
            )
        finally:
            queue.task_done()


async def run_on_projects(
    func: Callable[[GitLabAPI, Project, Any], Awaitable[Any]],
    *,
    url: str = "https://gitlab.com",
    requester: str = "gidgetlab-kit",
    access_token: Optional[str] = None,
    group: Optional[GitLabId],
    project_ids: List[GitLabId],
    nb_consumers: int = 5,
    **kwargs,
):
    """Run func on projects from group or list of ids

    project_ids has priority over group.
    A number of consumers are started to run the function in parallel on different projects.
    When creating Merge Requeests, it is recommended to keep that to 1 or 2.
    To gather information using GET requests, 5 or more is usually fine.
    """
    if group is None and not project_ids:
        raise ValueError("group or project_ids are mandatory")
    queue: asyncio.Queue[Project] = asyncio.Queue(maxsize=0)
    async with httpx.AsyncClient() as client:
        gl = GitLabAPI(client, requester, url=url, access_token=access_token)
        consumers = [
            asyncio.create_task(run_on_project(gl, queue, func, **kwargs))
            for _ in range(nb_consumers)
        ]
        if project_ids:
            projects = get_projects(gl, project_ids)
        elif group:
            projects = get_all_projects(gl, group)
        async for project in projects:
            await queue.put(project)
        await queue.join()
        for consumer in consumers:
            consumer.cancel()
