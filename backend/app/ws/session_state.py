from enum import Enum


class WSSessionState(str, Enum):
    CONNECTED = "CONNECTED"
    READY = "READY"
    CLOSED = "CLOSED"
