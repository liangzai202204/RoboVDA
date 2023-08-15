from enum import IntEnum


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
