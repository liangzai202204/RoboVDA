import os

from src.google.protobuf.json_format import ParseDict, Parse
from src.google.protobuf.text_format import Parse
from src.google.protobuf.message import Message


class Base:
    # 只能在子类中使用，子类中必须定义__obj__属性
    def __init__(self):
        self.__obj__: Message

    def __str__(self):
        return str(self.__obj__)

    def __repr__(self):
        return repr(self.__obj__)

    def load(self, js):
        if isinstance(js, dict):
            ParseDict(js, self.__obj__)
            return
        if isinstance(js, str):
            if os.path.isfile(js):
                with open(js, "r") as f:
                    js = f.read()
            Parse(js, self.__obj__)
            return
        self.__obj__.ParseFromString(js)
