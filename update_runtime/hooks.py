from blacksheep import Response

from src.interfaces.runtime import Service
from src.interfaces.types.types import SettingsMapper
from src.libs.api import json
from src.runtime.registry import ObjectsRegistry
from src.services.support.rtsp_workers_manager.rpc.rrc import (
    CloseStreamRtspWorkersManagerServiceRequest,
    CloseStreamRtspWorkersManagerServiceResponse,
    GetStreamRtspWorkersManagerServiceRequest,
    GetStreamRtspWorkersManagerServiceResponse,
)
from src.settings.settings import Settings

from .rrc import (
    CloseStreamRtspWorkersManagerHookRequest,
    GetStreamRtspWorkersManagerHookRequest,
)

# TODO
# content
# result = interactor_command_call (service name, content=repo_title)
# проверить есть ли хук на пару service name и repo title и
# если есть то вызывать его и результат передать в команду в content
# должен уметь рассчит параметры для ртсп потока и отдать их в сервис
# ртсп клиента через функцию command_call ( положить данные в data)
# service_name.command_call() == rcpclient()
# return


def close_stream(
    request: CloseStreamRtspWorkersManagerHookRequest,
    registry: ObjectsRegistry,
    service: Service,
) -> CloseStreamRtspWorkersManagerServiceResponse | Response:
    command_name = "close_stream"
    # service = registry.services.get("rtsp_workers_manager")

    response: CloseStreamRtspWorkersManagerServiceResponse = (
        service.client.command_call(
            command_name,
            CloseStreamRtspWorkersManagerServiceRequest(
                storage_title=request.storage_title,
            ),
        )
    )

    return response


def get_stream(
    request: GetStreamRtspWorkersManagerHookRequest,
    registry: ObjectsRegistry,
    service: Service,
    settings: Settings,
    mapper: SettingsMapper,
) -> GetStreamRtspWorkersManagerServiceResponse | Response:
    command_name = "get_stream"
    # service = registry.services.get("rtsp_workers_manager")

    # settings = registry.container.resolve(Settings)

    try:
        storage_config = settings.storages.get(request.storage_title)
    except Exception as exc:
        registry.logger.error(f"exc: {exc}")
        storage_config = None
    finally:
        if storage_config is None:
            return json(
                status=404,
                content=f"Storage with name {request.storage_title} didn't find",
            )

    response: GetStreamRtspWorkersManagerServiceResponse = service.client.command_call(
        command_name,
        GetStreamRtspWorkersManagerServiceRequest(
            storage_config_ref=type(storage_config).__module__,
            storage_config_title=type(storage_config).__name__,
            storage_config_data=mapper.dump(storage_config, storage_config.__class__),
        ),
    )
    return response
