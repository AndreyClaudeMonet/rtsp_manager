from blacksheep.server.openapi.common import EndpointDocs

from src.core.ext.update import ServiceHandlerInfo

from ..config import Config
from ..rpc.rrc import (
    CloseStreamRtspWorkersManagerServiceResponse,
    GetStreamRtspWorkersManagerServiceResponse,
)
from .hooks import close_stream, get_stream
from .rrc import (
    CloseStreamRtspWorkersManagerHookRequest,
    GetStreamRtspWorkersManagerHookRequest,
)


def update_service(c: Config) -> list[ServiceHandlerInfo]:
    ret = [
        ServiceHandlerInfo(
            name="get_stream",
            request_cls=GetStreamRtspWorkersManagerHookRequest,
            response_cls=GetStreamRtspWorkersManagerServiceResponse,
            handler=get_stream,
            schema=EndpointDocs(
                summary="Открытие трансляции видеопотока данных из shared memory",
                description="description",
            ),
        ),
        ServiceHandlerInfo(
            name="close_stream",
            request_cls=CloseStreamRtspWorkersManagerHookRequest,
            response_cls=CloseStreamRtspWorkersManagerServiceResponse,
            handler=close_stream,
            schema=EndpointDocs(
                summary="Закрытие трансляции видеопотока данных из shared memory",
                description="description",
            ),
        ),
    ]
    return ret
