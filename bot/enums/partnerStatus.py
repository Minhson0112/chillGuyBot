from enum import Enum


class PartnerStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
