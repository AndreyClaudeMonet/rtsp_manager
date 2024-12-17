from src.core.ext.container import DockerImageInfo, Py312BuildArgs
from src.settings.container import BuildDockerContainerConfig, DockerContainerConfig

Config = DockerContainerConfig
BuildConfig = BuildDockerContainerConfig[Py312BuildArgs]


def docker_info() -> DockerImageInfo:
    return DockerImageInfo(
        from_="py312",
        image="rtsp_workers_manager",
    )
