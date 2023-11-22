from src.parse_protobuf import message_rds_scene_pb2 as mspb
from src.parse_protobuf.define import scene_define as sdf
from src.parse_protobuf.base import Base


class Scene(sdf.Message_Scene, Base):

    def __init__(self, seer_scene=None):
        Base().__init__()
        self.__obj__: sdf.Message_Scene = mspb.Message_Scene()
        if seer_scene:
            self.load(seer_scene)

    #
    def __getattr__(self, item):
        return self.__obj__.__getattribute__(item)


