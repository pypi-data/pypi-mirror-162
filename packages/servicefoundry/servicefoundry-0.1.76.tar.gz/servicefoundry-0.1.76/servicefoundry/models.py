import os
import tempfile
from typing import Dict

from pydantic import BaseModel, constr

from servicefoundry.auto_gen.models import (
    Build,
    DockerFileBuild,
    LocalSource,
    RemoteSource,
    Service,
    TfyPythonBuild,
)
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.utils.file_utils import make_tarfile

# Evil
# This is happening because we are overloading DockerFileBuildConfig with two responsibilities.
#
# 1. Parse and validate arbitrary formats (JSON, YAML). In this case, type should be a required parameter.
# 2. Convenience class for the user, type should not be a required parameter.
#
# As DockerFileBuildConfig from CUE spec, it will follow (1).
# We can also solve this problem by adding a special constructor for the user. (Which is not a good experience).
# Or we add builder / getter functions for these class where the function will set the type while instantiating
# the class.


class Build(Build):
    type: constr(regex=r"build") = "build"


class DockerFileBuild(DockerFileBuild):
    type: constr(regex=r"dockerfile") = "dockerfile"


class TfyPythonBuild(TfyPythonBuild):
    type: constr(regex=r"tfy-python-buildpack") = "tfy-python-buildpack"


class Service(Service):
    type: constr(regex=r"service") = "service"


class Application(BaseModel):
    name: constr(regex=r"^[a-z0-9\-]+$")
    components: Dict[str, Service]


class RemoteSource(RemoteSource):
    type: constr(regex=r"remote") = "remote"


class LocalSource(LocalSource):
    type: constr(regex=r"local") = "local"

    def to_remote_source(
        self,
        workspace_fqn: str,
        component_name: str,
    ) -> RemoteSource:
        with tempfile.TemporaryDirectory() as local_dir:
            package_local_path = os.path.join(local_dir, "build.tar.gz")
            make_tarfile(
                output_filename=package_local_path,
                source_dir=self.project_root_path,
                additional_directories=[],
                ignore_list=[local_dir],
            )
            client = ServiceFoundryServiceClient.get_client()
            remote_uri = client.upload_code_package(
                workspace_fqn=workspace_fqn,
                component_name=component_name,
                package_local_path=package_local_path,
            )
            return RemoteSource(remote_uri=remote_uri)
