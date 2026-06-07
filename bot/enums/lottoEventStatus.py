from enum import Enum


class LottoEventStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    DRAWN = "drawn"
    CANCELLED = "cancelled"
