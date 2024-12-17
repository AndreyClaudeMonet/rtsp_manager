from importlib import import_module

from src.interfaces.infra.data_access.repo_intf import RepositoryIntf
from src.interfaces.models import ImageIntf
from src.service.registry import ServiceRegistry
from src.settings.container import AnyContainerConfig
from src.settings.mapper import settings_mapper
from src.settings.service import ServiceSettings

from ..config import Config
from ..context import RTSPWorkersManagerContext, StreamParams
from ..workers import GstRTSPWorker
from .rrc import (
    CloseStreamRtspWorkersManagerServiceRequest,
    CloseStreamRtspWorkersManagerServiceResponse,
    GetStreamRtspWorkersManagerServiceRequest,
    GetStreamRtspWorkersManagerServiceResponse,
)


def close_stream(
    request: CloseStreamRtspWorkersManagerServiceRequest,
    registry: ServiceRegistry,
) -> CloseStreamRtspWorkersManagerServiceResponse:
    """
    Функция удаления клиента для закрытия потока видео из разделяемой памяти
    """

    # получаем контекст и из него получаем параметры стрима
    context = registry.container.resolve(RTSPWorkersManagerContext)

    # завершаем клиента и удаляем данные из контекста
    try:
        params_stream = context.streams.pop(request.storage_title, None)

        if params_stream is None:
            return CloseStreamRtspWorkersManagerServiceResponse(
                message=f"There is no client streaming data from '{request.storage_title}'."
            )
        else:
            registry.futures.unregister(obj=params_stream.client, close=True)
            registry.servers.unregister(obj=params_stream.client, close=True)
            return CloseStreamRtspWorkersManagerServiceResponse(message="Success")

    except Exception as exc:
        registry.logger.error(
            f"During close stream exception is occured: {exc}", exc_info=exc
        )
        raise exc


def get_stream(
    request: GetStreamRtspWorkersManagerServiceRequest,
    registry: ServiceRegistry,
) -> GetStreamRtspWorkersManagerServiceResponse:
    """
    Функция создания клиента для получения потока видео из разделяемой памяти
    """

    # получаем класс shared mem и регистрируем его
    module = import_module(request.storage_config_ref)
    config_class = getattr(module, request.storage_config_title)
    mapper = settings_mapper()

    try:
        data = mapper.load(request.storage_config_data, config_class)
        registry.repo.register(data)
        repo: RepositoryIntf[ImageIntf] = registry.repo.get(data.name)
    except Exception as exc:
        registry.logger.error(
            f"During loading repository exception occured {exc}", exc_info=exc
        )
        return GetStreamRtspWorkersManagerServiceResponse(
            message=f"Cannot get repo with storage_config_data {request.storage_config_data}",
            rtsp_link=None,
            webrtc_link=None,
        )

    # формируем ссылку на поток
    settings = registry.container.resolve(ServiceSettings[Config, AnyContainerConfig])
    rtsp_link = f"rtsp://{settings.config.rtsp_server_ip}:{settings.config.rtsp_server_port}/{data.name}"
    webrtc_link = f"http://{settings.config.rtsp_server_ip}:{settings.config.webrtc_server_port}/{data.name}"

    # проверяем, что поток от такого shared mem не запущен
    context = registry.container.resolve(RTSPWorkersManagerContext)
    stream_params: StreamParams | None = context.streams.get(data.name, None)

    if stream_params is not None:
        if stream_params.client.name == repo.name:
            return GetStreamRtspWorkersManagerServiceResponse(
                message="Success",
                rtsp_link=rtsp_link,
                webrtc_link=webrtc_link,
            )
        else:
            return GetStreamRtspWorkersManagerServiceResponse(
                message="Address already used by another stream",
                rtsp_link=None,
                webrtc_link=None,
            )

    # создаем клиента для запуска потока
    client = GstRTSPWorker.build(
        rtsp_link=rtsp_link, name=rtsp_link, repo=repo, logger=registry.logger
    )
    context.streams[data.name] = StreamParams(
        client=client,
        rtsp_link=rtsp_link,
        webrtc_link=webrtc_link,
    )

    registry.servers.register(client)
    registry.futures.register(client)

    return GetStreamRtspWorkersManagerServiceResponse(
        message="Success",
        rtsp_link=rtsp_link,
        webrtc_link=webrtc_link,
    )
