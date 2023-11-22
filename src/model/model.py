import base64

from src.parse_protobuf.Model import Model

import json
import os

# 假设包 B 的名称为 package_B，JSON 文件名为 data.json
path_to_B = os.path.abspath("../model")
json_filename = 'robot.model'

json_file_path = os.path.join(path_to_B, json_filename)

with open(json_file_path, 'r',encoding="utf-8") as json_file:
    print(json_file)
    json_content = json.load(json_file)
m = Model(json_content)
for m_s in m.device_types:
    print(m_s.name)
    print(str(base64.b64decode(m_s.desc).decode()))
