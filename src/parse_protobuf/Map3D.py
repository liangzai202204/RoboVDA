from parse_protobuf import message_map_pb2 as mmpb
from parse_protobuf.define import map_define as mdf
from parse_protobuf.base import Base


class Map3D(mdf.Message_Map, Base):

    def __init__(self, seer_map=None):
        Base().__init__()
        self.__obj__: mdf.Message_Map3D = mmpb.Message_Map3D()
        if seer_map:
            self.load(seer_map)

    #
    def __getattr__(self, item):
        return self.__obj__.__getattribute__(item)


