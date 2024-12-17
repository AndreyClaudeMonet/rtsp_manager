from typing import Any, Protocol

from src.interfaces.infra import logger
from src.interfaces.infra.data_access.repo_intf import RepositoryIntf


class RTSPWorkerIntf(Protocol):
    def __init__(
        self,
        connection: Any,
        repo: RepositoryIntf[Any],
        name: str,
        logger: logger.Logger,
    ) -> None:
        ...

    @classmethod
    def build(
        cls,
        rtsp_link: str,
        name: str,
        repo: RepositoryIntf[Any],
        logger: logger.Logger,
    ) -> "RTSPWorkerIntf":
        ...

    @property
    def name(self) -> str:
        ...

    def start(self) -> None:
        ...

    def close(self) -> None:
        ...
