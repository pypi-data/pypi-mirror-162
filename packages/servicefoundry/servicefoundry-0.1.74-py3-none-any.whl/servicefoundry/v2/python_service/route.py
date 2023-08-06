import inspect
from typing import Callable, Dict, List

from pydantic import BaseModel, Field, constr

from servicefoundry.v2.python_service.remote import RemoteClass
from servicefoundry.v2.python_service.utils import get_qual_name


def path_pre_processor(path: str, prefix: str = "") -> str:
    path = path.strip("/")

    if not path:
        raise ValueError("path cannot be empty")

    prefix = prefix.strip("/")
    if not prefix:
        return f"/{path}"

    return f"/{prefix}/{path}"


class Route(BaseModel):
    function_name: str
    http_method: str
    path: constr(regex=r"^[A-Za-z0-9\-_/]+$")

    qual_name: str


class FunctionRoute(Route):
    module: str

    @classmethod
    def from_func(cls, func: Callable, path: str):

        return cls(
            function_name=func.__name__,
            http_method="POST",
            path=path_pre_processor(path or func.__name__),
            qual_name=get_qual_name(func),
            module=func.__module__,
        )


class ClassRoute(BaseModel):
    class_name: str
    init_kwargs: Dict = Field(default_factory=dict)
    module: str

    routes: List[Route] = Field(default_factory=list)

    @classmethod
    def from_class(cls, remote_class: RemoteClass):
        routes = []
        methods = inspect.getmembers(remote_class.class_, predicate=inspect.isfunction)

        for method_name, method in methods:
            if method_name.startswith("_"):
                continue
            route = Route(
                function_name=method_name,
                http_method="POST",
                path=path_pre_processor(prefix=remote_class.name, path=method_name),
                qual_name=remote_class.get_qual_name(method),
            )
            routes.append(route)

        return cls(
            class_name=remote_class.class_.__name__,
            init_kwargs=remote_class.init_kwargs,
            routes=routes,
            module=remote_class.class_.__module__,
        )


class RouteGroups(BaseModel):
    functions: List[FunctionRoute] = Field(default_factory=list)
    classes: Dict[str, ClassRoute] = Field(default_factory=dict)

    def register_function(self, func, path):
        self.functions.append(FunctionRoute.from_func(func=func, path=path))

    def register_class(self, remote_class: RemoteClass):
        if remote_class.name in self.classes:
            raise ValueError(
                f"name {remote_class.name!r} is already used to register a class"
            )
        self.classes[remote_class.name] = ClassRoute.from_class(remote_class)
