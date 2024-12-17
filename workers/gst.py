import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

import gi

from src.interfaces.infra import logger
from src.interfaces.infra.data_access.repo_intf import RepositoryIntf
from src.interfaces.models import ImageIntf

from .rtsp_worker_intf import RTSPWorkerIntf

gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
gi.require_version("GstApp", "1.0")
gi.require_version("GLib", "2.0")
from gi.repository import GLib, Gst, GstApp  # noqa: E402

Gst.init(sys.argv)


@dataclass
class UserData:
    repo: RepositoryIntf[ImageIntf]
    logger: logger.Logger


class PythonLogsLevels(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class GSTLogsLevels(Enum):
    NONE = 0
    ERROR = 1
    WARNING = 2
    FIXME = 3
    INFO = 4
    DEBUG = 5
    LOG = 6
    TRACE = 7
    MEMDUMP = 9


logs_levels_mapping: dict[int, int] = {
    PythonLogsLevels.DEBUG.value: GSTLogsLevels.DEBUG.value,
    PythonLogsLevels.INFO.value: GSTLogsLevels.INFO.value,
    PythonLogsLevels.WARNING.value: GSTLogsLevels.WARNING.value,
    PythonLogsLevels.ERROR.value: GSTLogsLevels.LOG.value,
    PythonLogsLevels.CRITICAL.value: GSTLogsLevels.MEMDUMP.value,
}


class GstRTSPWorker(RTSPWorkerIntf):
    def __init__(
        self,
        connection: Gst.Pipeline,
        repo: RepositoryIntf[ImageIntf],
        name: str,
        logger: logger.Logger,
    ) -> None:
        self._connection = connection
        self._repo = repo
        self._logger = logger
        self._loop = cast(GLib.MainLoop, None)
        self._name = name

    @classmethod
    def build(
        cls,
        rtsp_link: str,
        name: str,
        repo: RepositoryIntf[ImageIntf],
        logger: logger.Logger,
    ) -> "GstRTSPWorker":
        """
        Метод сборки клиента
        """

        # определяем уровень логгирования
        try:
            os.environ["GST_DEBUG"] = f"*:{logs_levels_mapping[logger.level]}"
        except KeyError as exc:
            logger.error(
                f"During set gst debug level exceptions occurs: {exc}", exc_info=exc
            )
            os.environ["GST_DEBUG"] = "*:0"

        # инициализируем параметры для создания пайплайна
        _source_image_shape = (repo.get()).image.shape
        _source_format = "BGR"
        _framerate = 30
        _bitrate = 2000
        _byte_stream_flag = "false"
        _key_int_max = 0
        _bframes = 0
        _tune_flag = "zerolatency"

        def get_frame(appsrc: GstApp.AppSrc, length: int, udata: UserData) -> Any:
            try:
                frame = repo.get().image[..., ::-1]
                appsrc.emit("push-buffer", Gst.Buffer.new_wrapped(frame.tobytes()))

            except Exception as exc:
                logger.error(
                    f"During get frame following exceptions occurs: {exc}", exc_info=exc
                )
                return Gst.FlowReturn.ERROR

            return Gst.FlowReturn.OK

        connection: Gst.Pipeline = Gst.parse_launch(
            f"appsrc name=source "
            f"! videoconvert ! video/x-raw, format=(string)I420 "
            f"! x264enc bitrate={_bitrate} byte-stream={_byte_stream_flag} "
            f"key-int-max={_key_int_max} bframes={_bframes} tune={_tune_flag} "
            f"! rtspclientsink location={rtsp_link}"
        )

        src: GstApp.AppSrc = connection.get_by_name("source")
        src.set_property("format", Gst.Format.TIME)
        src.set_property("do-timestamp", True)
        src.set_property(
            "caps",
            Gst.Caps.from_string(
                "video/x-raw, "
                f"width=(int){_source_image_shape[1]}, "
                f"height=(int){_source_image_shape[0]}, "
                f"format=(string){_source_format}, "
                f"framerate={_framerate}/1, "
            ),
        )

        udata = UserData(repo=repo, logger=logger)
        src.connect("need-data", get_frame, udata)

        return cls(connection=connection, repo=repo, name=name, logger=logger)

    @property
    def name(self) -> str:
        return self._name

    def start(self) -> None:
        try:
            _status = self._connection.set_state(Gst.State.PLAYING)

            if _status == Gst.StateChangeReturn.FAILURE:
                self._logger.error("Unable to set the pipeline to the playing state")
                raise RuntimeError

            self._loop = GLib.MainLoop()
            self._loop.run()

        except Exception as exc:
            self._logger.error(
                f"During starting {self.__class__.__name__} following exceptions occurs: {exc}",
                exc_info=exc,
            )
            self._loop.quit()
            raise exc

    def close(self) -> None:
        self._connection.set_state(Gst.State.NULL)
        self._loop.quit()
