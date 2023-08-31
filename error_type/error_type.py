from enum import IntEnum


class ErrorOrder(str):
    """
        topic : order error type
    """
    endNodeIdNotNodeId = "edge 的 endNodeId 不等于 NodeId"
    startNodeIdNotNodeId = "edge 的 startNodeId 不等于 NodeId"
    nodeAndEdgeNumErr = 0
    newOrderIdButOrderRunning = "下發新的 order ，但是已有 order"
    sendOrderToRobotErr = 2
    nodeOrEdgeEmpty = 3
    packNodeEdgeListErr = 4
    orderUpdateIdLowerErr = 5
    packTaskEdgeErr = 6
