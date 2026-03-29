from enum import IntEnum

class ModerationActionType(IntEnum):
    MUTE = 1
    KICK = 2
    BAN = 3
    PN = 4
    UNMUTE = 5
    DELMSG = 6