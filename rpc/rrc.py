from typing import Any

from src.libs.rpc.rrc import Tagged


class GetStreamRtspWorkersManagerServiceRequest(Tagged):
    storage_config_ref: str
    storage_config_title: str
    storage_config_data: dict[Any, Any]


class GetStreamRtspWorkersManagerServiceResponse(Tagged):
    message: str
    rtsp_link: str | None
    webrtc_link: str | None


class CloseStreamRtspWorkersManagerServiceRequest(Tagged):
    storage_title: str


class CloseStreamRtspWorkersManagerServiceResponse(Tagged):
    message: str
