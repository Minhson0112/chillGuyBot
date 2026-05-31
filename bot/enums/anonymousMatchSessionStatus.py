from enum import Enum


class AnonymousMatchSessionStatus(str, Enum):
    ACTIVE = "active"
    ENDING_REQUESTED = "ending_requested"
    ENDED = "ended"
