from src.core.const import ServiceStatus
from src.service.impl.context import Context
from src.service.registry import ServiceRegistry
from src.service.service import PreparedService, RpcHandlers
from src.settings.service import AnyContainerServiceSettings

from .config import Config
from .context import RTSPWorkersManagerContext
from .rpc.rpc import close_stream, get_stream


def setup(
    settings: AnyContainerServiceSettings[Config], registry: ServiceRegistry
) -> PreparedService[Context]:
    context = RTSPWorkersManagerContext()
    registry.container.add_instance(context)

    rpc_handlers: RpcHandlers = {"get_stream": get_stream, "close_stream": close_stream}

    return PreparedService(
        ServiceStatus.RUN,
        context,
        rpc_handlers=rpc_handlers,
    )
