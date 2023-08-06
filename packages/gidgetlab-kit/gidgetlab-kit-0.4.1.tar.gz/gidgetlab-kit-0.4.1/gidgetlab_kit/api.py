import asyncio
import base64
import http
import urllib.parse
import logging
from typing import Optional, Any, AsyncIterator, List, Dict
from gidgetlab import GitLabException, HTTPException
from gidgetlab.abc import GitLabAPI
from .models import Project, Group, GitLabId, Tag, TreeObject


logger = logging.getLogger(__name__)


def url_encode(s: str) -> str:
    """Return a url encoded string

    . is also replaced by %2E
    """
    return urllib.parse.quote(s, safe="").replace(".", "%2E")


def encode_gitlab_id(gitlab_id: GitLabId) -> str:
    """Return a URL encoded GitLab id"""
    if isinstance(gitlab_id, int):
        return str(gitlab_id)
    return url_encode(gitlab_id)


async def create_file_in_repository(
    gl: GitLabAPI,
    project_id: GitLabId,
    file_path: str,
    branch: str,
    start_branch: str,
    content: str,
    commit_message: str = "",
) -> Any:
    """Create a file in the project"""
    logger.info(f"Create {file_path} in project {project_id} branch {branch}")
    commit_message = commit_message or f"Add {file_path}"
    result = await gl.post(
        f"/projects/{project_id}/repository/files/{url_encode(file_path)}",
        data={
            "branch": branch,
            "start_branch": start_branch,
            "content": content,
            "commit_message": commit_message,
        },
    )
    return result


async def update_file_in_repository(
    gl: GitLabAPI,
    project_id: GitLabId,
    file_path: str,
    branch: str,
    start_branch: str,
    content: str,
    commit_message: str = "",
) -> Any:
    """Update a file in the project"""
    logger.info(f"Update {file_path} in project {project_id} branch {branch}")
    commit_message = commit_message or f"Update {file_path}"
    result = await gl.put(
        f"/projects/{project_id}/repository/files/{url_encode(file_path)}",
        data={
            "branch": branch,
            "start_branch": start_branch,
            "content": content,
            "commit_message": commit_message,
        },
    )
    return result


async def commit_file_in_repository(
    gl: GitLabAPI,
    project_id: GitLabId,
    file_path: str,
    branch: str,
    start_branch: str,
    content: str,
    commit_message: str,
) -> Any:
    """Create or update the file in the repository

    If the file doesn't exist, it will be created.
    If the file exists, it's updated only if the content differs.
    """
    try:
        existing_content = await get_file_from_repository(
            gl, project_id, file_path, ref=start_branch
        )
    except HTTPException as e:
        if e.status_code != http.HTTPStatus.NOT_FOUND:
            raise
        # The file doesn't exist
        result = await create_file_in_repository(
            gl, project_id, file_path, branch, start_branch, content, commit_message
        )
    else:
        # The file already exists
        if existing_content == content:
            logger.info("File content is identical. Nothing to commit.")
            return
        result = await update_file_in_repository(
            gl, project_id, file_path, branch, start_branch, content, commit_message
        )
    return result


async def unsubscribe_from_merge_request(
    gl: GitLabAPI, project_id: GitLabId, mr_iid: int
) -> Any:
    """Unsubscribes the authenticated user from a merge request to not receive notifications"""
    result = await gl.post(
        f"/projects/{project_id}/merge_requests/{mr_iid}/unsubscribe", data={}
    )
    return result


async def accept_merge_request(
    gl: GitLabAPI, project_id: GitLabId, mr_iid: int, **kwargs: Any
) -> Any:
    result = await gl.put(
        f"/projects/{project_id}/merge_requests/{mr_iid}/merge", data=kwargs
    )
    return result


async def create_merge_request(
    gl: GitLabAPI,
    project_id: GitLabId,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str = "",
    assignee_id: Optional[int] = None,
    remove_source_branch: bool = True,
    merge_on_success: bool = True,
    unsubscribe: bool = True,
) -> Any:
    logger.info(
        f"Create merge request '{title}' for project {project_id} from branch {source_branch} to {target_branch}"
    )
    data = {
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": title,
        "remove_source_branch": remove_source_branch,
    }
    if description:
        data["description"] = description
    if assignee_id is not None:
        data["assignee_id"] = assignee_id
    result = await gl.post(f"/projects/{project_id}/merge_requests", data=data)
    if unsubscribe:
        mr_iid = result["iid"]
        logger.info(f"Unsubscribe from merge request {mr_iid} for project {project_id}")
        await unsubscribe_from_merge_request(gl, project_id, mr_iid)
    if merge_on_success:
        # Wait to make sure the pipeline was created
        # The MR might be accepted directly otherwise
        await asyncio.sleep(5)
        mr_iid = result["iid"]
        logger.info(
            f"Accept merge request {mr_iid} for project {project_id} when pipeline succeeds"
        )
        await accept_merge_request(
            gl,
            project_id,
            mr_iid,
            merge_when_pipeline_succeeds=True,
            should_remove_source_branch=remove_source_branch,
        )
    return result


async def create_branch(
    gl: GitLabAPI, project_id: GitLabId, branch: str, ref: str
) -> Any:
    """Create a branch in the repository"""
    logger.info(f"Create branch {branch} in project {project_id} from {ref}")
    result = await gl.post(
        f"/projects/{project_id}/repository/branches",
        data={"branch": branch, "ref": ref},
    )
    return result


async def get_file_from_repository(
    gl: GitLabAPI, project_id: GitLabId, file_path: str, ref: str
) -> str:
    """Return the file from project as string"""
    result = await gl.getitem(
        f"/projects/{project_id}/repository/files/{url_encode(file_path)}",
        params={"ref": ref},
    )
    return base64.b64decode(result["content"]).decode("utf-8")


async def list_repository_tree(
    gl: GitLabAPI,
    project_id: GitLabId,
    ref: str,
    recursive: bool = True,
    path: Optional[str] = None,
) -> List[TreeObject]:
    params = {"ref": ref, "recursive": recursive}
    if path:
        params["path"] = path
    return [
        TreeObject(**repo_file)
        async for repo_file in gl.getiter(
            f"/projects/{project_id}/repository/tree",
            params=params,
        )
    ]


async def wait_for_merge_or_failure(
    gl: GitLabAPI, project_id: GitLabId, merge_request_iid: int, timeout: int = 600
) -> bool:
    """Wait for the merge request to be merged or the pipeline to fail"""
    logger.info(
        f"Wait for merge request {merge_request_iid} (project {project_id}) to be merged or pipeline to fail..."
    )
    mr_state = None
    pipeline_status = None
    sleep_time = 3
    max_loop = int(timeout / sleep_time)
    loop_nb = 0
    while (
        mr_state != "merged"
        and pipeline_status not in ("failed", "canceled")
        and loop_nb < max_loop
    ):
        loop_nb += 1
        await gl.sleep(sleep_time)
        result = await gl.getitem(
            f"/projects/{project_id}/merge_requests/{merge_request_iid}"
        )
        mr_state = result["state"]
        pipeline_status = result["head_pipeline"]["status"]
    logger.info(
        f"Merge request {merge_request_iid } state: {mr_state} / "
        f"Pipeline {result['head_pipeline']['id']} status: {pipeline_status}"
    )
    return mr_state == "merged"


async def update_file_via_merge_request(
    gl: GitLabAPI,
    project_id: GitLabId,
    file_path: str,
    content: str,
    source_branch: str,
    target_branch: str,
    message: str,
    description: str = "",
    assignee_id: Optional[int] = None,
    merge_on_success: bool = True,
    unsubscribe: bool = True,
    wait_on_merge: bool = False,
) -> None:
    await update_file_in_repository(
        gl, project_id, file_path, source_branch, target_branch, content, message
    )
    await asyncio.sleep(1)
    result = await create_merge_request(
        gl,
        project_id,
        source_branch,
        target_branch,
        title=message,
        description=description,
        assignee_id=assignee_id,
        merge_on_success=merge_on_success,
        unsubscribe=unsubscribe,
    )
    if wait_on_merge:
        if merge_on_success:
            await wait_for_merge_or_failure(gl, project_id, result["iid"])
        else:
            logger.warning(
                "wait_on_merge can only be set to True when merge_on_success is"
            )


async def get_projects(
    gl: GitLabAPI, project_ids: List[GitLabId]
) -> AsyncIterator[Project]:
    """Return projects based on their id"""
    for project_id in project_ids:
        project = await gl.getitem(f"/projects/{encode_gitlab_id(project_id)}")
        yield Project(**project)


async def get_all_projects(
    gl: GitLabAPI, group_id: GitLabId, archived: bool = False
) -> AsyncIterator[Project]:
    """Return all projects from a group, including subgroups"""
    async for project in gl.getiter(
        f"/groups/{encode_gitlab_id(group_id)}/projects", params={"archived": archived}
    ):
        yield Project(**project)
    async for subgroup in get_subgroups(gl, group_id):
        async for project in gl.getiter(
            f"/groups/{subgroup.id}/projects", params={"archived": archived}
        ):
            yield Project(**project)


async def get_subgroups(gl: GitLabAPI, group_id: GitLabId) -> AsyncIterator[Group]:
    """Return recursively all subgroups from a group"""
    async for subgroup in gl.getiter(f"/groups/{encode_gitlab_id(group_id)}/subgroups"):
        yield Group(**subgroup)
        async for sub in get_subgroups(gl, subgroup["id"]):
            yield sub


async def find_projects(
    gl: GitLabAPI, names: List[str], group_id: GitLabId
) -> List[Project]:
    """Find the projects based on their name under `group_id`

    The group's subgroups are also searched
    Return the list of projects found
    """
    names_set = {name.lower() for name in names}
    all_projects = [project async for project in get_all_projects(gl, group_id)]
    return [project for project in all_projects if project.name.lower() in names_set]


async def create_project_trigger(
    gl: GitLabAPI, project_id: GitLabId, description: str
) -> str:
    """Create a project trigger and return the corresponding token"""
    result = await gl.post(
        f"/projects/{project_id}/triggers", data={"description": description}
    )
    return result["token"]


async def get_project_triggers(
    gl: GitLabAPI, project_id: GitLabId
) -> List[Dict[str, str]]:
    """Return the project triggers"""
    return [trigger async for trigger in gl.getiter(f"/projects/{project_id}/triggers")]


async def get_or_create_project_trigger_token(
    gl: GitLabAPI, project_id: GitLabId, description: str
) -> str:
    """Return a trigger token for the project

    If no existing token is found for the given description, one is created
    """
    triggers = await get_project_triggers(gl, project_id)
    tokens = [
        trigger["token"]
        for trigger in triggers
        if trigger["description"] == description
    ]
    if tokens:
        return tokens[0]
    return await create_project_trigger(gl, project_id, description)


async def trigger_pipeline(
    gl: GitLabAPI, project_id: GitLabId, git_ref: str, token: str
) -> None:
    """Trigger the project pipeline"""
    await gl.post(
        f"/projects/{project_id}/trigger/pipeline",
        params={"token": token, "ref": git_ref},
        data={},
    )


async def list_branches(gl: GitLabAPI, project_id: GitLabId) -> List[str]:
    """Return the list of branches name"""
    return [
        branch["name"]
        async for branch in gl.getiter(f"/projects/{project_id}/repository/branches")
    ]


async def list_tags(gl: GitLabAPI, project_id: GitLabId) -> List[Tag]:
    """Return the list of tags sorted by updated field"""
    return [
        Tag(**data)
        async for data in gl.getiter(
            f"/projects/{project_id}/repository/tags",
            params={"order_by": "updated", "sort": "desc"},
        )
    ]


async def get_latest_tag_on_branch(
    gl: GitLabAPI, project_id: GitLabId, branch: str = "master"
) -> Optional[Tag]:
    """Return the latest updated tag of branch"""
    # Get all tags
    tags = await list_tags(gl, project_id)
    # Check that the tag is on the proper branch
    for tag in tags:
        async for ref in gl.getiter(
            f"/projects/{project_id}/repository/commits/{tag.target}/refs",
            params={"type": "branch"},
        ):
            if ref["type"] == "branch" and ref["name"] == branch:
                return tag
    return None


async def trigger_pipelines(
    gl: GitLabAPI,
    projects: List[Project],
    description: str,
    git_refs: Optional[List[str]] = None,
) -> None:
    """Trigger the pipeline for all projects

    If no git ref is given, the pipeline is triggered for the default branch only
    """
    for project in projects:
        if project.default_branch is None:
            # Project is empty - skip it
            continue
        try:
            token = await get_or_create_project_trigger_token(
                gl, project.id, description
            )
        except GitLabException as e:
            logger.error(f"Couldn't get project {project.name} trigger token: {e}")
            continue
        if git_refs is None:
            project_git_refs = [project.default_branch]
        else:
            project_git_refs = git_refs
        for git_ref in project_git_refs:
            try:
                await trigger_pipeline(gl, project.id, git_ref, token)
            except GitLabException as e:
                logger.error(
                    f"Couldn't trigger project {project.name} pipeline for {git_ref}: {e}"
                )
