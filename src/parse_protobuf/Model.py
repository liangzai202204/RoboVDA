from src.parse_protobuf import message_model_pb2 as mmpb
from src.parse_protobuf.define import model_define as mdf
from src.parse_protobuf.base import Base


class Model(mdf.Message_Model, Base):

    def __init__(self, seer_model=None):
        Base().__init__()
        self.__obj__: mdf.Message_Model = mmpb.Message_Model()
        if seer_model:
            self.load(seer_model)

    #
    def __getattr__(self, item):
        return self.__obj__.__getattribute__(item)