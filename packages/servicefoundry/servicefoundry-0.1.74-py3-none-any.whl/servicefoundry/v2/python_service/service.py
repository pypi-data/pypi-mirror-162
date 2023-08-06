import sys
from typing import Callable, List, Optional

import yaml
from pydantic import BaseModel

from servicefoundry.auto_gen.models import Port, Resources
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.lib.dao.workspace import get_workspace
from servicefoundry.models import (
    Application,
    Build,
    LocalSource,
    Service,
    TfyPythonBuild,
)
from servicefoundry.v2.python_service.app import build_and_run_app_in_background_thread
from servicefoundry.v2.python_service.remote import RemoteClass
from servicefoundry.v2.python_service.route import RouteGroups
from servicefoundry.version import __version__


class BuildConfig(BaseModel):
    python_version: str = f"{sys.version_info.major}.{sys.version_info.minor}"
    pip_packages: Optional[List[str]]
    requirements_path: Optional[str] = None

    def __init__(self, **data):
        pip_packages = data.get("pip_packages", [])
        # locally version == 0.0.0
        # pip_packages.append(f"servicefoundry=={__version__}")
        pip_packages.append("servicefoundry")
        data["pip_packages"] = pip_packages
        super().__init__(**data)

    def to_tfy_python_build_config(
        self, port: int, route_groups: RouteGroups
    ) -> TfyPythonBuild:
        return TfyPythonBuild(
            python_version=self.python_version,
            pip_packages=self.pip_packages,
            requirements_path=self.requirements_path,
            # May need to handle escaping in "{route_groups.json()}"
            command=f'python -m servicefoundry.v2.python_service run --port {port} --route-group-json "{route_groups.json()}"',
        )


class PythonService:
    def __init__(
        self,
        name: str,
        ###
        # Maybe be this should be present in the `deploy` function.
        #
        build_config: BuildConfig = BuildConfig(),
        resources: Resources = Resources(),
        replicas: int = 1,
        port: int = 8000
        ###
    ):
        self._name = name
        self._build_config = build_config
        self._resources = resources
        self._replicas = replicas
        self._port = port

        self._route_groups: RouteGroups = RouteGroups()

    @property
    def route_groups(self) -> RouteGroups:
        return self._route_groups

    def __repr__(self):
        return yaml.dump(
            dict(
                name=self._name,
                build_config=self._build_config.dict(),
                resources=self._resources.dict(),
                routes=self._route_groups.dict(),
                replicas=self._replicas,
                port=self._port,
            ),
            indent=2,
        )

    def register_function(
        self,
        func: Callable,
        path: Optional[str] = None,
    ):
        self._route_groups.register_function(func=func, path=path)

    def register_class(self, remote_class: RemoteClass):
        self._route_groups.register_class(remote_class=remote_class)

    def run(self) -> "threading.Thread":
        return build_and_run_app_in_background_thread(
            route_groups=self._route_groups, port=self._port
        )

    def _to_service_spec(self) -> Service:
        tfy_python_build_config = self._build_config.to_tfy_python_build_config(
            port=self._port, route_groups=self._route_groups
        )
        service = Service(
            image=Build(build_source=LocalSource(), build_spec=tfy_python_build_config),
            resources=self._resources,
            replicas=self._replicas,
            ports=[Port(port=self._port, expose=True)],
        )
        return service

    def deploy(self, workspace_fqn: str):
        service_spec = self._to_service_spec()
        workspace_id = get_workspace(workspace_fqn).id

        service_spec.image.build_source = (
            service_spec.image.build_source.to_remote_source(
                workspace_fqn=workspace_fqn, component_name=self._name
            )
        )

        application = Application(
            name=self._name, components={self._name: service_spec}
        )
        print(yaml.dump(application.dict(exclude_none=True), indent=1))
        print(application.json(exclude_none=True, indent=1))

        client = ServiceFoundryServiceClient.get_client()
        response = client.deploy_application(
            workspace_id=workspace_id, application=application
        )
        print(response)
