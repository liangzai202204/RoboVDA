import pydantic


class Connection(pydantic.BaseModel):
    headerId: int = 0
    timestamp: str = ""
    version: str = "2.0.0"
    manufacturer: str = ""
    serialNumber: str = ""
    connectionState: str = ""

    @staticmethod
    def create() -> "Connection":
        return Connection(headerId=0,
                          timestamp="",
                          version="2.0.0",
                          manufacturer="",
                          serialNumber="",
                          connectionState="")

