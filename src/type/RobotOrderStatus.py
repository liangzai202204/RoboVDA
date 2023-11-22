from enum import IntEnum, Enum


class RobotOrderStatus(IntEnum):
    StatusNone = 0
    Waiting = 1
    Running = 2
    Suspended = 3
    Completed = 4
    Failed = 5
    Canceled = 6
    OverTime = 7
    NotFound = 404


class Status(str, Enum):
    WAITING = "WAITING"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"