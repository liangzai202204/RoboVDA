import enum
from typing import List

import pydantic


class ActionParameter(pydantic.BaseModel):
    key: str
    value: str


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


class InstantActions(pydantic.BaseModel):
    headerId: int = 0
    timestamp: str = ""
    version: str = "2.0.0"
    manufacturer: str = ""
    serialNumber: str = ""
    actions: List[Action] = []
