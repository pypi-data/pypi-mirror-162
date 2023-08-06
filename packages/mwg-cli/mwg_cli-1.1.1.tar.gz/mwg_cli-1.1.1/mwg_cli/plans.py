import os
from subprocess import CalledProcessError, run

from . import git
from .exceptions import LoggedError

BUCKET = "aaa-terraform-state"


class PlanNotFound(LoggedError):
    def __init__(self, obj: str) -> None:
        super().__init__(f"Could not find plan object {obj}")


def upload(workspace: str, filename: str) -> None:
    object_url = _object_url(workspace, filename)
    cmd = ["gsutil", "cp", filename, object_url]
    run(cmd, check=True)
    print(f"Uploaded plan to {object_url}")


def download(workspace: str, filename: str) -> None:
    object_url = _object_url(workspace, filename)
    cmd = ["gsutil", "cp", object_url, filename]
    try:
        run(cmd, check=True)
    except CalledProcessError:
        raise PlanNotFound(object_url)
    print(f"Downloaded plan {object_url}")


def _object_url(workspace: str, filename: str) -> str:
    basename = os.path.basename(filename)
    repo = git.get_repo_name()
    return f"gs://{BUCKET}/{repo}/plans/{workspace}/{basename}"
