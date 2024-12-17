from src.libs.rpc.rrc import Tagged


class GetStreamRtspWorkersManagerHookRequest(Tagged):
    storage_title: str


class CloseStreamRtspWorkersManagerHookRequest(Tagged):
    storage_title: str
