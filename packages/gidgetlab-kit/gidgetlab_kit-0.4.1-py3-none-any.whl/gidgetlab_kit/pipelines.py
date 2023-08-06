import datetime
import random
import typer
from operator import itemgetter
from typing import List
from dateutil.parser import parse
from dateutil.tz import UTC
from gidgetlab.abc import GitLabAPI
from .models import GitLabId, Project
from . import api


async def get_project_latest_pipeline_date(
    gl: GitLabAPI, project_id: GitLabId
) -> datetime.datetime:
    """Return the project latest pipeline execution date"""
    # pipelines are returned sorted by desc id by default
    # Highest id is the latest
    pipelines = await gl.getitem(f"/projects/{project_id}/pipelines")
    try:
        latest_pipeline = pipelines[0]
    except IndexError:
        return datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=UTC)
    return parse(latest_pipeline["updated_at"])


async def sort_projects_by_pipeline_date(
    gl: GitLabAPI, projects: List[Project]
) -> List[Project]:
    """Return the projects sorted by latest pipeline execution date"""
    # Build a list of tuple with each project and the latest pipeline date
    project_pipelines = [
        (project, await get_project_latest_pipeline_date(gl, project.id))
        for project in projects
    ]
    sorted_project_pipelines = sorted(project_pipelines, key=itemgetter(1))
    return [item[0] for item in sorted_project_pipelines]


async def run_trigger_group_pipelines(
    gl: GitLabAPI,
    group: GitLabId,
    nb_projects: int,
    is_random: bool = False,
    description: str = "gidgetlab",
    exclude: List[str] = [],
) -> None:
    """Trigger the pipeline for the group projects

    When greater than 0, nb_projects allows to select a subset of the projects.
    If is_random is true, projects are picked randomly. If not, the ones with
    the oldest pipeline execution are selected.
    Some projects can be excluded based on the path with namespace.
    """
    # Filter out empty project (default_branch is None) and excluded one
    projects = [
        project
        async for project in api.get_all_projects(gl, group)
        if project.default_branch is not None
        and project.path_with_namespace not in exclude
    ]
    if nb_projects == 0 or nb_projects >= len(projects):
        sampled = projects
    else:
        if is_random:
            sampled = random.sample(projects, nb_projects)
        else:
            sorted_projects = await sort_projects_by_pipeline_date(gl, projects)
            sampled = sorted_projects[:nb_projects]
    typer.secho(
        f"Trigger pipeline for {' '.join([project.name for project in sampled])}",
        fg=typer.colors.GREEN,
    )
    await api.trigger_pipelines(gl, sampled, description)
    await gl._client.aclose()
