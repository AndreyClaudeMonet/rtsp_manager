from subprocess import DEVNULL, PIPE, Popen

from src.interfaces.infra import logger
from src.interfaces.infra.data_access.repo_intf import RepositoryIntf
from src.interfaces.models import ImageIntf

from .rtsp_worker_intf import RTSPWorkerIntf


class FFmpegRTSPWorker(RTSPWorkerIntf):
    def __init__(
        self,
        connection: Popen[bytes],
        repo: RepositoryIntf[ImageIntf],
        name: str,
        logger: logger.Logger,
    ) -> None:
        self._connection = connection
        self._repo = repo
        self._logger = logger
        self._running = False
        self._name = name

    @classmethod
    def build(
        cls,
        rtsp_link: str,
        name: str,
        repo: RepositoryIntf[ImageIntf],
        logger: logger.Logger,
    ) -> "FFmpegRTSPWorker":
        _source_image_shape = (repo.get()).image.shape

        _input_pix_fmt = "bgr24"
        _size = f"{_source_image_shape[1]}x{_source_image_shape[0]}"
        _bitrate = "512k"
        _bufsize = "1M"
        _output_pix_fmt = "yuv420p"
        _vcodec = "libx264"
        _rtsp_transport = "udp"

        ffmpeg_command = [
            "ffmpeg",
            "-re",
            "-f",
            "rawvideo",
            "-pix_fmt",
            _input_pix_fmt,
            "-s",
            _size,
            "-i",
            "pipe:",
            "-f",
            "rtsp",
            "-b:v",
            _bitrate,
            "-bufsize",
            _bufsize,
            "-preset",
            "ultrafast",
            "-pix_fmt",
            _output_pix_fmt,
            "-vcodec",
            _vcodec,
            "-rtsp_transport",
            _rtsp_transport,
            rtsp_link,
        ]

        connection = Popen(
            ffmpeg_command,
            stdin=PIPE,
            stderr=DEVNULL,
        )

        instance = cls(connection, repo, name, logger)

        return instance

    @property
    def name(self) -> str:
        return self._name

    def start(self) -> None:
        if self._running:
            return

        self._running = True

        while self._running:
            try:
                _frame = self._repo.get().image[..., ::-1]
                self._connection.stdin.write(_frame.tobytes())  # type: ignore[union-attr]
            except Exception as exc:
                self._logger.error(
                    f"During starting {self.__class__.__name__} following exceptions occurs: {exc}",
                    exc_info=exc,
                )
                raise exc

    def close(self) -> None:
        self._running = False
        self._connection.kill()
