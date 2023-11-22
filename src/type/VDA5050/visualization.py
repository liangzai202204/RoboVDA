import pydantic
from src.type.VDA5050 import state


class Visualization(pydantic.BaseModel):
    headerId: int = 0
    timestamp: str = ""
    version: str = "2.0.0"
    manufacturer: str = "SEER"
    serialNumber: str = ""
    agvPosition: state.AgvPosition
    velocity: state.Velocity

    @staticmethod
    def create() -> "Visualization":
        return Visualization(headerId=0,
                             timestamp="",
                             version="2.0.0",
                             manufacturer="",
                             serialNumber="",
                             agvPosition={"x": 0.,
                                          "y": 0.,
                                          "theta": 0.,
                                          "mapId": "",
                                          "positionInitialized": False},
                             velocity={"vx": 0.,
                                       "vy": 0.,
                                       "omega": 0., })
