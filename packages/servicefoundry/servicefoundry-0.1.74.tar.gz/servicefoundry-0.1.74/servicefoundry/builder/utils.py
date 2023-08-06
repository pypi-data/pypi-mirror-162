import os
from typing import Optional

from servicefoundry.sfy_build_pack_common.process_util import execute


def get_expanded_and_absolute_path(path: str):
    return os.path.abspath(os.path.expanduser(path))


def build_docker_image(tag: str, path: str = ".", file: Optional[str] = None):
    path = get_expanded_and_absolute_path(path)

    # TODO: use the official SDK from docker
    # https://docker-py.readthedocs.io/en/stable/

    cmd = ["docker", "build", path, "-t", tag]
    if file:
        file = get_expanded_and_absolute_path(file)
        cmd.extend(["--file", file])
    for line in execute(cmd):
        print(line)
