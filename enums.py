
from enum import Enum

class Status(Enum):
    IDLE = 1
    IN_USE = 2
    MAINTENANCE = 3

class Direction(Enum):
    UP = 1
    DOWN = 2