from pydantic import BaseModel, HttpUrl
from typing import Optional, Union


GitLabId = Union[int, str]


# "full_path": "my-group",
# "id": 214,
# "kind": "group",
# "name": "my-group",
# "parent_id": null,
# "path": "my-group",
# "web_url": "https://gitlab.com/groups/my-group"
class Namespace(BaseModel):
    """GitLab Namespace"""

    id: int = -1
    name: str
    kind: str = ""
    web_url: Optional[HttpUrl] = None
    path: str = ""
    full_path: str = ""
    parent_id: Optional[int] = None

    def __str__(self) -> str:
        return self.name


# "id": 2701,
# "name": "my-cool-project",
# "description": "",
# "web_url": "https://gitlab.com/test-group/subgroup-1/my-cool-project",
# "git_ssh_url": "git@gitlab.com:test-group/subgroup-1/my-cool-project.git",
# "git_http_url": "https://gitlab.com/test-group/subgroup-1/my-cool-project.git",
# "namespace": "subgroup-1",
# "visibility_level": 0,
# "path_with_namespace": "test-group/subgroup-1/my-cool-project",
# "default_branch": "master",
class Project(BaseModel):
    """GitLab Project"""

    # Some fields are set to a default value
    # to easily create a Project manually (not from
    # a webhook or API call)
    id: int = -1
    name: str
    # description can be None
    description: Optional[str] = ""
    web_url: Optional[HttpUrl] = None
    # webhook events return git_ssh_url / git_http_url
    # as well as ssh_url / http_url
    git_ssh_url: str = ""
    git_http_url: Optional[HttpUrl] = None
    # /projects API returns ssh_url_to_repo / http_url_to_repo
    ssh_url_to_repo: str = ""
    http_url_to_repo: Optional[HttpUrl] = None
    # webhook events return a string
    # /projects API returns a Namespace
    namespace: Union[str, Namespace]
    visibility_level: int = 0
    path_with_namespace: str = ""
    # default_branch is None when the project is empty
    default_branch: Optional[str] = "master"

    class Config:
        extra = "allow"

    @property
    def base_namespace(self) -> str:
        if "/" not in self.path_with_namespace:
            return str(self.namespace)
        return self.path_with_namespace.split("/", 1)[0]

    @property
    def ssh_url(self) -> str:
        return self.ssh_url_to_repo or self.git_ssh_url

    @property
    def http_url(self) -> Optional[HttpUrl]:
        return self.http_url_to_repo or self.git_http_url

    def __str__(self) -> str:
        return self.name


class Group(BaseModel):
    """GitLab Group"""

    id: int = -1
    name: str
    web_url: Optional[HttpUrl] = None
    path: str
    description: str = ""
    full_name: str
    full_path: str
    parent_id: Optional[int] = None

    def __str__(self) -> str:
        return self.name


class Tag(BaseModel):
    """Project Tag"""

    name: str
    target: str


class TreeObject(BaseModel):
    """Tree Object"""

    id: str
    name: str
    type: str
    path: str
    mode: str
