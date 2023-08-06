import asyncio
from typing import List
from gidgetlab.abc import GitLabAPI
from .models import GitLabId, Project
from . import api


async def produce_projects(
    gl: GitLabAPI, queue: asyncio.Queue, group_id: GitLabId, archived: bool
) -> List[Project]:
    """Send to the queue all projects from the group, including subgroups

    Return the full list of projects when done
    """
    projects = []
    async for project in api.get_all_projects(gl, group_id, archived):
        projects.append(project)
        await queue.put(project)
    return projects
