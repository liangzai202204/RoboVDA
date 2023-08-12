import pydantic
from type import state


class Visualization(pydantic.BaseModel):
    headerId: int = 0
    timestamp: str = ""
    version: str = "2.0.0"
    manufacturer: str = "SEER"
    serialNumber: str = ""
    agvPosition: state.AgvPosition
    velocity: state.Velocity

    @staticmethod
    def create(args) -> "Visualization":
        return Visualization(**args)



