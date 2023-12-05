from typing import List, Optional
import pydantic


class TypeSpecification(pydantic.BaseModel):
    seriesName: Optional[str] = ''
    seriesDescription: Optional[str] = ''
    agvKinematic: Optional[str] = ''  # DIFF, OMNI, THREE WHEEL
    agvClass: Optional[str] = ''  # FORKLIFT, CONVEYOR, TAGGER, CARRIER
    maxLoadMass: Optional[float] = 0.
    localizationTypes: Optional[List[str]] = ''  # NATURAL, REFLECTOR, RFID, DMC, SPOT, GRID
    navigationTypes: Optional[List[str]] = ''  # PHYSICAL_LINE_GUIDED, VIRTUAL_LINE_GUIDED, AUTONOMOUS


class PhysicalParameters(pydantic.BaseModel):
    speedMin: Optional[float] = 0.
    speedMax: Optional[float] = 0.
    accelerationMax: Optional[float] = 0.
    decelerationMax: Optional[float] = 0.
    heightMin: Optional[float] = 0.
    heightMax: Optional[float] = 0.
    width: Optional[float] = 0.
    length: Optional[float] = 0.


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
    maxStringLens: Optional[MaxStringLens]
    maxArrayLens: Optional[MaxArrayLens]
    timing: Optional[Timing]


class OptionalParameter(pydantic.BaseModel):
    parameter: Optional[str]
    support: Optional[str]
    description: Optional[str]


class AGVActionParameter(pydantic.BaseModel):
    key: Optional[str]
    valueDataType: Optional[str]
    description: Optional[str]
    isOptional: Optional[bool]


class AGVAction(pydantic.BaseModel):
    actionType: Optional[str]
    actionDescription: Optional[str]
    actionScopes: Optional[List[str]]
    actionParameters: Optional[List[AGVActionParameter]] = None
    resultDescription: Optional[str] = None


class ProtocolFeatures(pydantic.BaseModel):
    optionalParameters: Optional[List[OptionalParameter]] = None
    agvActions: Optional[List[AGVAction]] = None


class WheelDefinition(pydantic.BaseModel):
    type: Optional[str]
    isActiveDriven: Optional[bool]
    isActiveSteered: Optional[bool]
    position: Optional[dict]
    diameter: Optional[float]
    width: Optional[float]
    centerDisplacement: Optional[float]


class Envelope2D(pydantic.BaseModel):
    set: Optional[str]
    polygonPoints: Optional[List[dict]]
    description: Optional[str]


class Envelope3D(pydantic.BaseModel):
    set: Optional[str]
    format: Optional[str]
    data: Optional[dict]
    url: Optional[str]
    description: Optional[str]


class AgvGeometry(pydantic.BaseModel):
    wheelDefinitions: Optional[List[WheelDefinition]]
    envelopes2d: Optional[List[Envelope2D]]
    envelopes3d: Optional[List[Envelope3D]]


class LoadSet(pydantic.BaseModel):
    setName: Optional[str]
    loadType: Optional[str]
    loadPositions: Optional[List[str]]
    boundingBoxReference: Optional[dict]
    loadDimensions: Optional[dict]
    maxWeight: Optional[float]
    minLoadhandlingHeight: Optional[float]
    maxLoadhandlingHeight: Optional[float]
    minLoadhandlingDepth: Optional[float]
    maxLoadhandlingDepth: Optional[float]
    minLoadhandlingTilt: Optional[float]
    maxLoadhandlingTilt: Optional[float]
    agvSpeedLimit: Optional[float]
    agvAccelerationLimit: Optional[float]
    agvDecelerationLimit: Optional[float]
    pickTime: Optional[float]
    dropTime: Optional[float]
    description: Optional[str]


class LoadSpecification(pydantic.BaseModel):
    loadPositions: Optional[List[str]]
    loadSets: Optional[List[LoadSet]]


class LocalizationParameters(pydantic.BaseModel):
    pass


class FactSheet(pydantic.BaseModel):
    headerId: Optional[int] = 0
    timestamp: Optional[str] = ""
    version: Optional[str] = ""
    manufacturer: Optional[str] = ""
    serialNumber: Optional[str] = ''
    typeSpecification: Optional[TypeSpecification] = TypeSpecification()
    physicalParameters: Optional[PhysicalParameters] = PhysicalParameters()
    protocolLimits: Optional[ProtocolLimits] = None
    protocolFeatures: Optional[ProtocolFeatures] = None
    agvGeometry: Optional[AgvGeometry] = None
    loadSpecification: Optional[LoadSpecification] = None
    localizationParameters: Optional[LocalizationParameters] = None
