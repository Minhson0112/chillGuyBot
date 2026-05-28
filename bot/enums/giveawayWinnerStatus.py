from enum import Enum


class GiveawayWinnerStatus(str, Enum):
    SELECTED = "selected"
    CLAIMED = "claimed"
    DISQUALIFIED = "disqualified"
    REROLLED = "rerolled"
