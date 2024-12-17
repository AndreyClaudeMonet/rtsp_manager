from dataclasses import dataclass

from src.settings.service import ServiceConfig, Storages


@dataclass(kw_only=True)
class Config(ServiceConfig[Storages[None], None]):
    rtsp_server_ip: str
    rtsp_server_port: int
    webrtc_server_port: int
