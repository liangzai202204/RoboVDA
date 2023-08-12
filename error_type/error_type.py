from enum import IntEnum


class ErrorOrder(IntEnum):
    """
        topic : order error type
    """
    nodeAndEdgeNumErr = 0
    newOrderIdButOrderRunning = 1
    sendOrderToRobotErr = 2
    nodeOrEdgeEmpty = 3
    packNodeEdgeListErr = 4
    orderUpdateIdLowerErr = 5
    packTaskEdgeErr = 6
