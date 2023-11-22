from src.parse_protobuf import message_map_pb2 as mmpb
from src.parse_protobuf.define import map_define as mdf
from src.parse_protobuf.base import Base


class Map2D(mdf.Message_Map, Base):

    def __init__(self, seer_map=None):
        Base().__init__()
        self.__obj__: mdf.Message_Map = mmpb.Message_Map()
        if seer_map:
            self.load(seer_map)

    #
    def __getattr__(self, item):
        return self.__obj__.__getattribute__(item)


