from my_module import normal, uniform

from servicefoundry.v2.python_service import BuildConfig, PythonService, Resources

random_service = PythonService(
    name="random_service",
    build_config=BuildConfig(pip_packages=["numpy<1.22.0"]),
    resources=Resources(cpu_limit="500m", memory_limit="512Mi"),
    replicas=2,
    port=4000,
)
random_service.register_function(normal)
random_service.register_function(uniform)

print(random_service)

random_service.run().join()
