from enum import Enum


class ServerInviteStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DELETED = "deleted"
    UNKNOWN = "unknown"
