from enum import Enum


class ToolStatus(str, Enum):
    AVAILABLE = "available"
    EQUIPPED = "equipped"
    BROKEN = "broken"