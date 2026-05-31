from enum import Enum


class AnonymousMatchQueueStatus(str, Enum):
    WAITING = "waiting"
    MATCHED = "matched"
    CANCELLED = "cancelled"
