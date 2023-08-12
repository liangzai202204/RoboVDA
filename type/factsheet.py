from typing import List, Optional
import pydantic


class TypeSpecification(pydantic.BaseModel):
    seriesName: str
    seriesDescription: str
    agvKinematic: str  # DIFF, OMNI, THREE WHEEL
    agvClass: str  # FORKLIFT, CONVEYOR, TAGGER, CARRIER
    maxLoadMass: float
    localizationTypes: List[str]  # NATURAL, REFLECTOR, RFID, DMC, SPOT, GRID
    navigationTypes: List[str]  # PHYSICAL_LINE_GUIDED, VIRTUAL_LINE_GUIDED, AUTONOMOUS


class PhysicalParameters(pydantic.BaseModel):
    speedMin: float
    speedMax: float
    accelerationMax: float
    decelerationMax: float
    heightMin: float
    heightMax: float
    width: float
    length: float


class MaxStringLens(pydantic.BaseModel):
    msgLen: Optional[int] = 0
    topicSerialLen: Optional[int] = 0
    topicElemLen: Optional[int] = 0
    idLen: Optional[int] = 0
    idNumericalOnly: Optional[bool] = False
    enumLen: Optional[int] = 0
    loadIdLen: Optional[int] = 0


class MaxArrayLens(pydantic.BaseModel):
    orderNodes: Optional[int] = 0
    orderEdges: Optional[int] = 0
    nodeActions: Optional[int] = 0
    edgeActions: Optional[int] = 0
    actionsParameters: Optional[int] = 0
    instantActions: Optional[int] = 0
    trajectoryKnotVector: Optional[int] = 0
    trajectoryControlPoints: Optional[int] = 0
    stateNodeStates: Optional[int] = 0
    stateEdgeStates: Optional[int] = 0
    stateLoads: Optional[int] = 0
    stateActionStates: Optional[int] = 0
    stateErrors: Optional[int] = 0
    stateInformations: Optional[int] = 0
    errorErrorReferences: Optional[int] = 0
    informationsInfoReferences: Optional[int] = 0


class Timing(pydantic.BaseModel):
    minOrderInterval: Optional[float] = 0.0
    minStateInterval: Optional[float] = 0.0
    defaultStateInterval: Optional[float] = 0.0
    visualizationInterval: Optional[float] = 0.0


class ProtocolLimits(pydantic.BaseModel):
    maxStringLens: MaxStringLens
    maxArrayLens: MaxArrayLens
    timing: Timing


class OptionalParameter(pydantic.BaseModel):
    parameter: str
    support: str
    description: str


class AGVActionParameter(pydantic.BaseModel):
    key: str
    valueDataType: str
    description: str
    isOptional: bool


class AGVAction(pydantic.BaseModel):
    actionType: str
    actionDescription: str
    actionScopes: List[str]
    actionParameters: Optional[List[AGVActionParameter]] = None
    resultDescription: Optional[str] = None


class ProtocolFeatures(pydantic.BaseModel):
    optionalParameters: Optional[List[OptionalParameter]] = None
    agvActions: Optional[List[AGVAction]] = None


class WheelDefinition(pydantic.BaseModel):
    type: str
    isActiveDriven: bool
    isActiveSteered: bool
    position: dict
    diameter: float
    width: float
    centerDisplacement: Optional[float]


class Envelope2D(pydantic.BaseModel):
    set: str
    polygonPoints: List[dict]
    description: str


class Envelope3D(pydantic.BaseModel):
    set: str
    format: str
    data: dict
    url: str
    description: str


class AgvGeometry(pydantic.BaseModel):
    wheelDefinitions: List[WheelDefinition]
    envelopes2d: List[Envelope2D]
    envelopes3d: List[Envelope3D]


class LoadSet(pydantic.BaseModel):
    setName: str
    loadType: str
    loadPositions: Optional[List[str]]
    boundingBoxReference: dict
    loadDimensions: dict
    maxWeight: float
    minLoadhandlingHeight: float
    maxLoadhandlingHeight: float
    minLoadhandlingDepth: float
    maxLoadhandlingDepth: float
    minLoadhandlingTilt: float
    maxLoadhandlingTilt: float
    agvSpeedLimit: float
    agvAccelerationLimit: float
    agvDecelerationLimit: float
    pickTime: float
    dropTime: float
    description: str


class LoadSpecification(pydantic.BaseModel):
    loadPositions: List[str]
    loadSets: List[LoadSet]


class LocalizationParameters(pydantic.BaseModel):
    pass


class Factsheet(pydantic.BaseModel):
    headerId: int
    timestamp: str
    version: str
    manufacturer: str
    serialNumber: str
    typeSpecification: Optional[TypeSpecification]
    physicalParameters: PhysicalParameters
    protocolLimits: ProtocolLimits
    protocolFeatures: ProtocolFeatures
    agvGeometry: AgvGeometry
    loadSpecification: LoadSpecification
    localizationParameters: LocalizationParameters
