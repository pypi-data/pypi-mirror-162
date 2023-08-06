from servicefoundry.auto_gen.models import DockerFileBuild, TfyPythonBuild, constr

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


class DockerFileBuild(DockerFileBuild):
    type: constr(regex=r"dockerfile") = "dockerfile"


class TfyPythonBuild(TfyPythonBuild):
    type: constr(regex=r"tfy-python-buildpack") = "tfy-python-buildpack"
