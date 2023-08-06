from enum import Enum


class TrafficType(Enum):
    UNKNOWN = 0
    PRODUCTION = 1
    REPLAY = 2
    SHADOW = 4
