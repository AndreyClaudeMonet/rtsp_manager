from dataclasses import dataclass, field

from src.service.impl.context import Context
from src.services.support.rtsp_workers_manager.workers import RTSPWorkerIntf


@dataclass
class StreamParams:
    client: RTSPWorkerIntf
    rtsp_link: str
    webrtc_link: str


class RTSPWorkersManagerContext(Context, kw_only=True):
    streams: dict[str, StreamParams] = field(default_factory=dict)
