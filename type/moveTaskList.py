import json
from typing import List, Optional, Union
from pydantic import BaseModel


class ControlPoints(BaseModel):
    x: float
    y: float
    weight: Optional[float] = 1.0


class Trajectory(BaseModel):
    type: Optional[str] = "CubicBeizer"
    degree:Optional[int] = 1
    knotVector: List[int] = []
    controlPoints: List[ControlPoints]


class TargetPos(BaseModel):
    x: float
    y: float
    theta: float


class SourcePos(BaseModel):
    x: float
    y: float
    theta: float


class Task(BaseModel):
    id: str
    targetPos: TargetPos
    source_id: str
    sourcePos: SourcePos
    task_id: str
    trajectory: Trajectory
    operation: Optional[str] = ""
    script_args: Optional[dict] ={}
    script_name: Optional[str] = ""
    script_stage: Optional[int] = 2


class MoveTaskList(BaseModel):
    move_task_list: Optional[List[Task]] = []


# JSON数据
# json_data = {
#     "move_task_list": [
#         {
#             "id": "LM2",
#             "targetPos": {
#                 "x": 12.5,
#                 "y": 1.5,
#                 "theta": 0.0
#             },
#             "source_id": "LM1",
#             "sourcePos": {
#                 "x": 0.0,
#                 "y": 0.0,
#                 "theta": 0.0
#             },
#             "task_id": "abcd",
#             "trajectory": {
#                 "type": "NURBS",
#                 "degree": 1,
#                 "knotVector": [0, 0, 1, 1],
#                 "controlPoints": [
#                     {
#                         "x": 0.0,
#                         "y": 0.0,
#                         "weight": 1.0
#                     },
#                     {
#                         "x": 12.5,
#                         "y": 1.5,
#                         "weight": 1.0
#                     }
#                 ]
#             }
#         },
#         {
#             "id": "LM3",
#             "targetPos": {
#                 "x": 20,
#                 "y": 1.5,
#                 "theta": 0.0
#             },
#             "source_id": "LM2",
#             "sourcePos": {
#                 "x": 12.5,
#                 "y": 1.5,
#                 "theta": 0.0
#             },
#             "task_id": "abcd2",
#             "trajectory": {
#                 "type": "Straight",
#                 "controlPoints": [
#                     {
#                         "x": 12.5,
#                         "y": 1.5
#                     },
#                     {
#                         "x": 12.5,
#                         "y": 1.5
#                     }
#                 ]
#             }
#         },
#         {
#             "id": "LM4",
#             "targetPos": {
#                 "x": 40,
#                 "y": 2.5,
#                 "theta": 0.0
#             },
#             "source_id": "LM3",
#             "sourcePos": {
#                 "x": 20,
#                 "y": 1.5,
#                 "theta": 0.0
#             },
#             "task_id": "abcd3",
#             "trajectory": {
#                 "type": "CubicBeizer",
#                 "controlPoints": [
#                     {
#                         "x": 20,
#                         "y": 1.5
#                     },
#                     {
#                         "x": 20,
#                         "y": 1.5
#                     },
#                     {
#                         "x": 40,
#                         "y": 2.5
#                     },
#                     {
#                         "x": 40,
#                         "y": 2.5
#                     }
#                 ]
#             }
#         }
#     ]
# }
#
# # 解析JSON数据并转换为Connection对象列表
# connections = MoveTaskList(**json_data)
# # M = Task()
# # M.task_id=";;;;"
#
#
#
# # 打印Connection对象列表
# print(json.dumps(connections.model_dump()))
