import enum
from typing import List, Optional, Union
from src.type import state
import pydantic


class Header:
    headerId: int
    timestamp: str
    version: str
    manufacturer: str
    serialNumber: str


class ActionParameter(pydantic.BaseModel):
    key: str
    value: Union[str,float,int]


class ActionBlockingType(str, enum.Enum):
    NONE = "NONE"
    SOFT = "SOFT"
    HARD = "HARD"


class Action(pydantic.BaseModel):
    actionType: str
    actionId: str
    blockingType: ActionBlockingType = ActionBlockingType.HARD
    actionParameters: List[ActionParameter] = []
    actionDescription: str = ""

    @staticmethod
    def creat() -> "Action":
        return Action(
            actionType="",
            actionId="",
            blockingType=ActionBlockingType.HARD,
            actionParameters=[],
            actionDescription=""

        )


class NodePosition(pydantic.BaseModel):
    x: float
    y: float
    theta: float
    allowedDeviationXY: float = 0.0
    allowedDeviationTheta: float = 0.0
    mapId: str = ""
    mapDescription: str = ""


class Node(pydantic.BaseModel):
    nodeId: str
    sequenceId: int
    released: bool = True
    nodePosition: Optional[NodePosition]
    actions: List[Action] = []
    nodeDescription: str = ""

    class Config:
        arbitrary_types_allowed = True


class Edge(pydantic.BaseModel):
    edgeId: str
    sequenceId: int
    edgeDescription: str = ""
    released: bool = True
    startNodeId: str
    endNodeId: str
    maxSpeed: Optional[float] = 0.
    maxHeight: Optional[float] = 0.
    orientation: Optional[float] = 0.
    holdDir: Optional[float] = None
    direction: Optional[str] = ""
    rotationAllowed: Optional[bool] = False
    maxRotationSpeed: Optional[float] = 0.
    trajectory: Optional[state.Trajectory] = None
    length: Optional[float] = None
    actions: List[Action] = []


class Order(pydantic.BaseModel):
    headerId: int = 0
    timestamp: str = ""
    version: str = "2.0.0"
    manufacturer: str = ""
    serialNumber: str = ""
    orderId: str
    orderUpdateId: int
    nodes: List[Node]
    edges: List[Edge]

    @staticmethod
    def create_order(task: "Order") -> "Order":
        # 检验 task 的内容 todo
        return Order(**task.model_dump())
