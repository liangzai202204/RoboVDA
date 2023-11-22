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
    mapNotNodePosition = "地图没有这个点"
    actionPackEmpty = "打包动作为空"
    orderNodeGetMapPointErr = "order 的 nodePosition 在地图中找不到对应点"


class ErrorPckTask(str):
    """
        topic : order error type
    """
    MapNotPoint = None
    endNodeIdNotNodeId = "edge 的 endNodeId 不等于 NodeId"
    startNodeIdNotNodeId = "edge 的 startNodeId 不等于 NodeId"
    nodeAndEdgeNumErr = 0
    sendOrderToRobotErr = 2
    nodeOrEdgeEmpty = 3
    packNodeEdgeListErr = 4
    orderUpdateIdLowerErr = 5
    packTaskEdgeErr = 6
    mapNotNodePosition = "地图没有这个点"
