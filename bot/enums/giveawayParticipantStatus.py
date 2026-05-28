from enum import Enum


class GiveawayParticipantStatus(str, Enum):
    ACTIVE = "active"
    REMOVED = "removed"
    INVALID = "invalid"
