from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


class NodePosition(BaseModel):
    x: float
    y: float
    theta: float
    allowedDeviationXY: float = 0.0
    allowedDeviationTheta: float = 0.0
    mapId: str = ""
    mapDescription: str = ""


class NodeState(BaseModel):
    nodeId: str
    sequenceId: int
    released: bool = True
    # opt
    nodeDescription: Optional[str]
    nodePosition: Optional[NodePosition]

    @staticmethod
    def create_node_state() -> "NodeState":
        return NodeState(nodeId="",
                         sequenceId=0,
                         release=True,
                         nodeDescription="",
                         nodePosition=NodePosition(x=0.,
                                                   y=0.,
                                                   theta=0.0,
                                                   mapId="",
                                                   allowedDeviationXY=0.,
                                                   allowedDeviationTheta=0.,
                                                   mapDescription=""))


class KnotVectorItem(BaseModel):
    type: float
    maximum: float = 1.0
    minimum: float = 0.0


class ControlPoint(BaseModel):
    x: float
    y: float
    weight: Optional[float] = 1.0


class Trajectory(BaseModel):
    type: Optional[str] = ""
    degree: Optional[int] = 1
    knotVector: Optional[List[KnotVectorItem]] = []
    controlPoints: Optional[List[ControlPoint]] = []


class EdgeState(BaseModel):
    edgeId: str
    sequenceId: int
    released: bool = True
    edgeDescription: Optional[str]
    trajectory: Optional[Trajectory]

    @staticmethod
    def create() -> "EdgeState":
        return EdgeState(edgeId="",
                         sequenceId=0,
                         release=True,
                         edgeDescription="",
                         trajectory={})


class ActionStatus(str, Enum):
    """
    "description":
    "WAITING: waiting for the trigger (passing the mode, entering the edge)
    PAUSED: paused by instantAction or external trigger
    FAILED: action could not be performed.",

    """
    WAITING = "WAITING"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


class ActionState(BaseModel):
    actionId: str
    actionStatus: Optional[ActionStatus] = ActionStatus.INITIALIZING
    actionType: Optional[str] = ""
    actionDescription: Optional[str] = ""
    resultDescription: Optional[str] = ""

    @staticmethod
    def creat_action_state() -> "ActionState":
        return ActionState(actionId="",
                           actionStatus=ActionStatus.WAITING,
                           actionType="",
                           actionDescription="",
                           resultDescription=""
                           )


class AgvPosition(BaseModel):
    x: float
    y: float
    theta: float
    mapId: str
    positionInitialized: bool
    mapDescription: Optional[str] = ""
    localizationScore: Optional[float] = 0.
    deviationRange: Optional[float] = 0.


class ErrorLevel(str, Enum):
    """
    description
    "WARNING: AGV is ready to start (e.g., maintenance cycle expiration warning).
    FATAL: AGV is not in running condition, user intervention required (e.g., laser scanner is contaminated).",
    """
    WARNING = "WARNING"
    FATAL = "FATAL"


class ErrorReference(BaseModel):
    referenceKey: str
    referenceValue: str


class Error(BaseModel):
    errorType: str  # Type/name of error
    errorLevel: ErrorLevel = ErrorLevel.WARNING
    errorReferences: Optional[List[ErrorReference]] = []
    errorDescription: Optional[str] = ""

    @staticmethod
    def create_error() -> "Error":
        return Error(errorType="",
                     errorLevel=ErrorLevel.WARNING,
                     errorReferences=[],
                     errorDescription="")


class BatteryState(BaseModel):
    """
    电池信息
    """
    batteryCharge: float
    charging: bool
    batteryVoltage: Optional[float] = 0.
    batteryHealth: Optional[float] = 0.

    reach: Optional[float] = 0.  # "Estimated reach with current State of Charge in meter.",


class InfoReference(BaseModel):
    referenceKey: str
    referenceValue: str


class InfoLevel(str, Enum):
    """
    "description":
    "DEBUG: used for debugging.
    INFO: used for visualization."
    """
    INFO = "INFO"
    DEBUG = "DEBUG"


class Information(BaseModel):
    """
    用于可视化，不用于实际运单
    """
    infoType: str = ""
    infoLevel: InfoLevel = InfoLevel.INFO
    infoReferences: Optional[List[InfoReference]] = []
    infoDescription: Optional[str] = ""


class EStop(str, Enum):
    """
    Acknowledge-Type of eStop:
    AUTOACK: auto-acknowledgeable e-stop is activated, e.g., by bumper or protective field.
    MANUAL: e-stop hast to be acknowledged manually at the vehicle.
    REMOTE: facility e-stop has to be acknowledged remotely.
    NONE: no e-stop activated.
    """
    AUTOACK = "AUTOACK"
    MANUAL = "MANUAL"
    REMOTE = "REMOTE"
    NONE = "NONE"


class SafetyState(BaseModel):
    eStop: EStop = EStop.NONE
    fieldViolation: bool = False


class OperatingMode(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    SEMIAUTOMATIC = "SEMIAUTOMATIC"
    MANUAL = "MANUAL"
    SERVICE = "SERVICE"
    TEACHIN = "TEACHIN"


class Velocity(BaseModel):
    vx: float
    vy: float
    omega: float


class BoundingBoxReference(BaseModel):
    x: float
    y: float
    z: float
    theta: Optional[float]


class LoadDimensions(BaseModel):
    length: float
    width: float
    height: Optional[float]


class Load(BaseModel):
    loadId: str
    loadType: str
    loadPosition: str
    boundingBoxReference: Optional[BoundingBoxReference]
    loadDimensions: Optional[LoadDimensions]
    weight: float = 0.0


class State(BaseModel):
    """
    数据链路：AGV -> master
    机器人对主控的状态反馈
    """
    headerId: int
    timestamp: str
    version: str = "2.0.0"
    manufacturer: str = ""
    serialNumber: str = ""
    orderId: str = ""
    orderUpdateId: int = 0
    zoneSetId: str = ""
    lastNodeId: str = ""
    lastNodeSequenceId: int = 0
    nodeStates: List[NodeState]
    edgeStates: List[EdgeState]
    driving: bool = False
    waitingForInteractionZoneRelease: bool = False
    paused: Optional[bool] = False
    newBaseRequest: Optional[bool] = False
    actionStates: List[ActionState] = []
    batteryState: BatteryState
    operatingMode: OperatingMode = OperatingMode.AUTOMATIC
    agvPosition: AgvPosition
    velocity: Velocity
    loads: Optional[List[Load]] = []
    errors: List[Error] = []
    safetyState: SafetyState
    information: List[Information] = []

    @staticmethod
    def create_state() -> "State":
        return State(
            headerId=0,
            timestamp="",
            version="2.0.0",
            manufacturer="SEER",
            serialNumber="",
            orderId="",
            orderUpdateId=0,
            zoneSetId="",
            lastNodeId="",
            lastNodeSequenceId=0,
            nodeStates=[],
            edgeStates=[],
            driving=False,
            actionStates=[],
            batteryState=BatteryState(batteryCharge=0.,
                                      charging=False,
                                      batteryVoltage=0.),
            agvPosition={"x": 0.,
                         "y": 0.,
                         "theta": 0.,
                         "mapId": "",
                         "positionInitialized": False},
            velocity={"vx": 0., "vy": 0., "omega": 0.},
            loads=[],
            errors=[],
            safetyState={},
            information=[]
        )


if __name__ == "__main__":
    b = State()
