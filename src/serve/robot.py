import asyncio
import json
import os
import queue
import datetime

import src.rbklib.rbklibPro
from src.serve.topicQueue import TopicQueue
from src.type.VDA5050 import state, factsheet
from typing import List
from src.type.pushMsgType import RobotPush
from src.type.ApiReq import ApiReq
from src.log.log import MyLogger
from src.parse_protobuf.Model import Model
from src.parse_protobuf.Map2D import Map2D


class Robot:

    def __init__(self, rbk: src.rbklib.rbklibPro):

        self.rbk = rbk
        self.robot_type = 0  # 车子的类型，0：没有类型，1：fork，2：jack，3：hook，等。这个参数用于任务打包
        self.task_status: asyncio.Queue[dict] = asyncio.Queue()
        self.ApiReq_queue: asyncio.Queue[ApiReq] = asyncio.Queue()
        self.model = RobotModel(rbk)
        self.map = RobotMap(rbk)
        self.logs = MyLogger()
        self.robot_push_msg = RobotPush
        self.init = False
        # 電池狀態
        self.battery_state = state.BatteryState
        # 機器人位置
        self.agv_position = state.AgvPosition
        self.state = state.State.create_state()
        self.nick_name = "vda5050"
        self.lock = False
        self.localizationTypes = ["SLAM"]
        self.factsheet = None
        self.params = {}
        self.messages = queue.Queue()

    async def run(self):
        while True:
            if self.robot_online:
                if self.init:
                    await self.update()
                else:
                    self.map.get_map()
                    self.lock_robot()
                    self.model.get_model()
                    self._get_params()
                    self.init = True
                # self.logs.info(f'[robot]online status:{self.rbk.online_status}')
            else:
                await asyncio.sleep(1)
                self.logs.info(f"[robot]robot not on line ,waiting 1 s")

    @property
    def robot_online(self) -> bool:
        """
        check robot online status,and check robot lock status
        :return:
        """
        if self.rbk.online:
            return True
        return False

    async def update(self):
        push_data = None
        """
        将机器人的数据，更新到 self.state 中
        :return:
        """
        try:
            push_data = await TopicQueue.pushData.get()
            new_push_ata = RobotPush(**json.loads(push_data))
            # self.logs.info(f"[robot][19301] push raw data ok.|{new_push_ata.model_dump().__len__()}")
            if push_data:
                self.robot_push_msg = new_push_ata
                # state
                self.update_state()
                # 根據信息判斷邏輯
                # 控制權
                self.update_lock()
                # 當前地圖
                self.update_map()
                # 依次爲：在綫、控制權、定位、置信度、任務狀態、目標點
                # self.logs.info(
                #     f'[robot]robot status:{self.robot_online}|{self.lock}|{self.robot_push_msg.reloc_status}|'
                #     f'{self.robot_push_msg.confidence}|{self.robot_push_msg.task_status}|'
                #     f'{self.robot_push_msg.target_id}')
                # 定位信息
        except queue.Empty:
            # 如果队列为空，则跳过本次循环，继续等待下一个数据
            self.logs.error(f"19301 push data is Empty,pass")
        except Exception as e:
            self.logs.error(f"json.loads(push_data)：{e},{push_data}")

    def update_state(self):
        self.state.headerId += 1
        self.state.timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z'
        self.state.batteryState = self.battery_state(
            batteryCharge=self.robot_push_msg.battery_level,
            charging=self.robot_push_msg.charging,
            batteryVoltage=self.robot_push_msg.voltage
        )
        # 操作模式
        self.state.operatingMode = self.update_operating_mode()
        # 位置信息
        self.state.agvPosition = self.agv_position(x=self.robot_push_msg.x,
                                                   y=self.robot_push_msg.y,
                                                   theta=self.robot_push_msg.angle,
                                                   mapId=self.robot_push_msg.current_map,
                                                   positionInitialized=True if (
                                                           self.robot_push_msg.reloc_status == 2 or
                                                           self.robot_push_msg.reloc_status == 4) else False,
                                                   deviationRange=0.,
                                                   localizationScore=self.robot_push_msg.confidence,
                                                   mapDescription="")
        # 机器人名称、rbk版本
        self.state.serialNumber = self.robot_push_msg.vehicle_id
        self.state.version = self.robot_push_msg.version
        self.state.loads = [] if not self.robot_push_msg.goods_region.point else self.update_goods()
        self.state.driving = False if self.robot_push_msg.is_stop else True
        self.state.paused = True if self.robot_push_msg.task_status == 3 else False
        self.state.waitingForInteractionZoneRelease = False  # TODO
        self.state.velocity = state.Velocity(vx=self.robot_push_msg.vx,
                                             vy=self.robot_push_msg.vy,
                                             omega=self.robot_push_msg.w)
        # 更新 error seer

        # self.state.errors = self.update_errors()

    def update_goods(self):

        goods = self.robot_push_msg.goods_region
        load_goods = state.Load()
        load_goods.loadId = goods.name
        load_goods.loadType = goods.name
        load_goods.loadPosition = str(goods.point)
        return [load_goods]

    def update_operating_mode(self) -> state.OperatingMode:
        mode = state.OperatingMode.MANUAL
        if self.robot_online and self.is_lock_control:
            mode = state.OperatingMode.AUTOMATIC
        if not self.is_lock_control:
            mode = state.OperatingMode.SERVICE
        return mode

    def update_errors(self) -> List[state.Error]:
        def err(ers: list, e_list: list, level):
            errs = e_list
            for er in ers:
                f_child = state.Error()
                for key, value in er.items():
                    if key not in ["desc", "times"]:
                        f_child.errorType = key
                    if key in ["desc"]:
                        f_child.errorDescription = value
                    f_child.errorLevel = level
                errs.append(f_child)

        err_list = []
        if self.robot_push_msg:
            if self.robot_push_msg.fatals:
                err(self.robot_push_msg.fatals, err_list, state.ErrorLevel.FATAL)
            if self.robot_push_msg.errors:
                err(self.robot_push_msg.errors, err_list, state.ErrorLevel.FATAL)
            if self.robot_push_msg.warnings:
                err(self.robot_push_msg.warnings, err_list, state.ErrorLevel.WARNING)
            if self.robot_push_msg.notices:
                err(self.robot_push_msg.notices, err_list, state.ErrorLevel.WARNING)
        return err_list

    @property
    def is_lock_control(self) -> bool:
        if not self.robot_online:
            return False
        return self.robot_push_msg.current_lock.nick_name == self.nick_name

    def update_lock(self):
        if self.is_lock_control:
            return
        else:
            if not self.robot_push_msg.current_lock.locked:
                self.lock_robot()

    def update_map(self):
        if not self.map.current_map_md5:
            self.map.current_map_md5 = self.robot_push_msg.current_map_md5
        if self.robot_push_msg.current_map != self.map.current_map or self.map.current_map_md5 != self.robot_push_msg.current_map_md5:
            self.logs.info(f"[map]current_map:{self.robot_push_msg.current_map}||{self.map.current_map}"
                           f"current_map_md5:{self.robot_push_msg.current_map_md5}||")
            self.map.get_map(self.robot_push_msg.current_map)
            self.map.current_map_md5 = self.robot_push_msg.current_map_md5

    def lock_robot(self):
        if self.robot_online:
            # self.rbk.robot_config_lock_req(self.nick_name)
            self.rbk.call_service(ApiReq.ROBOT_CONFIG_LOCK_REQ.value, {"nick_name": self.nick_name})
            self.logs.info("master has lock")

    def get_task_status(self, edges_id_list):
        res_edges_json = self.rbk.call_service(ApiReq.ROBOT_STATUS_TASK_STATUS_PACKAGE_REQ.value,
                                               {"task_ids": edges_id_list})
        res_edges = json.loads(res_edges_json)
        if res_edges:
            task_status = res_edges["task_status_package"]["task_status_list"]

            return task_status

    def set_push(self):
        self.rbk.call_service(ApiReq.ROBOT_PUSH_CONFIG_REQ.value,
                              {"interval": 100})

    def send_order(self, task_list):
        try:
            if not isinstance(task_list, list) or not task_list:
                self.logs.error(f"send_order is empty:{task_list}")
                return
        except Exception as e:
            self.logs.error(f"收到訂單,发送失败:{e}")
        move_task_list = {
            'move_task_list': task_list
        }
        flag = True
        try:
            while flag:
                if self.is_lock_control:
                    # res_data = self.rbk.request(3066, msg=move_task_list)
                    res_data = self.rbk.call_service(ApiReq.ROBOT_TASK_GOTARGETLIST_REQ.value, move_task_list)
                    res_data_json = json.loads(res_data)
                    self.logs.info(f"下发任务内容：{move_task_list}, rbk 返回结果：{res_data_json}")
                    if res_data_json["ret_code"] == 0:
                        self.logs.info(f"下发任务成功：{move_task_list}")
                        flag = False
                    else:

                        self.lock_robot()
                        self.logs.info(f"下发任务失败：{move_task_list}")

                else:
                    self.logs.info("没有控制权，无法下发任务")
        except Exception as e:
            self.logs.info(f"试图抢占控制权并下发任务失败，可能是没有链接到机器人,{e}")

    def _send_robot_service_request(self, service_name: str) -> bool:
        """发送机器人服务请求"""
        send = True
        while send:
            try:
                if self.robot_online and self.is_lock_control:
                    res = self.rbk.call_service(service_name)
                    res_json = json.loads(res)
                    print(res_json)

                    if "ret_code" in res_json:
                        if res_json["ret_code"] == 0:
                            send = False
                else:
                    self.lock_robot()
            except Exception as e:
                self.logs.error(f"[robot]service request error:{e}")
                return False
        return True

    def instant_stop_pause(self):
        """暂停机器人任务"""
        return self._send_robot_service_request(ApiReq.ROBOT_TASK_RESUME_REQ.value)

    def instant_start_pause(self):
        """恢复机器人任务"""
        return self._send_robot_service_request(ApiReq.ROBOT_TASK_PAUSE_REQ.value)

    def instant_cancel_task(self) -> bool:
        """取消机器人任务"""
        return self._send_robot_service_request(ApiReq.ROBOT_TASK_CLEARTARGETLIST_REQ.value)

    def instant_init_position(self, task):
        self.send_order(task)
        return True

    def get_fact_sheet(self) -> factsheet.Factsheet:
        f = factsheet.Factsheet()
        f.typeSpecification.seriesName = self.robot_push_msg.vehicle_id
        f.typeSpecification.seriesDescription = self.robot_push_msg.vehicle_id
        if self.model.mode == "differential" or self.model.mode == "dualDiff":
            f.typeSpecification.agvKinematic = "DIFF"
        if self.model.mode == "multiSteers":
            f.typeSpecification.agvKinematic = "OMNI"
        if self.model.mode == "steer":
            f.typeSpecification.agvKinematic = "STEER"
        if self.model.mode == "RGV2" or self.model.mode == "RGV4":
            f.typeSpecification.agvKinematic = "RGV"
        f.typeSpecification.agvClass = self.model.agvClass
        f.typeSpecification.maxLoadMass = 0.5
        f.typeSpecification.localizationTypes = self.localizationTypes if self.model.pgv_func else \
            not self.localizationTypes.append(self.model.pgv_func)
        f.typeSpecification.navigationTypes = "VIRTUAL_LINE_GUIDED"

        f.physicalParameters.speedMin = 0.01
        f.physicalParameters.speedMax = self.params.get("MoveFactory", {}).get("MaxSpeed", {}).get("value", 0)
        f.physicalParameters.accelerationMax = self.params.get("MoveFactory", {}).get("Load_MaxAcc", {}).get("value", 0)
        f.physicalParameters.decelerationMax = self.params.get("MoveFactory", {}).get("Load_MaxDec", {}).get("value", 0)
        f.physicalParameters.heightMin = self.model.height
        f.physicalParameters.heightMax = self.model.height
        f.physicalParameters.width = self.model.width
        f.physicalParameters.length = self.model.length
        return f

    def _get_params(self):
        try:
            par_req = self.rbk.call_service(ApiReq.ROBOT_STATUS_PARAMS_REQ.value, {"plugin": "MoveFactory"})
            if not par_req:
                self.logs.error(f"req error")
                return {}
            self.params = json.loads(par_req)
            self.logs.info(f"model_req len :{len(par_req)}")

        except OSError as o:
            self.logs.error(f"_get_params:{o}")
            return {}
        except Exception as e:
            self.logs.error(f"_get_params:{e}")
        return None


class RobotModel:
    def __init__(self, rbk):
        self.height = 0
        self.length = 0
        self.width = 0
        self.pgv_func = None
        self.pgv = "NONE"
        self.mode = "NONE"
        self.agvClass = "NONE"
        self.model_dir = os.path.join("/usr/local/SeerRobotics/vda/", "robotModel")
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        self.model_path = os.path.join(self.model_dir, "robot.model")
        self.rbk = rbk
        self.model = None
        self.mode = None
        self.log = MyLogger()
        self.model_msg = {}

    def _get_model(self):
        try:
            model_req = self.rbk.call_service(ApiReq.ROBOT_STATUS_MODEL_REQ.value)
            if not model_req:
                self.log.error(f"req error")
                return {}
            self.log.info(f"model_req len :{len(model_req)}")
            # print(self.model_path)
            # 将模型文件写入硬盘
            with open(self.model_path, 'wb') as file:
                # 可选：写入内容到文件
                file.write(model_req)
                self.log.info(f"[robot] load model OK!")
            # 解析模型文件
            return json.loads(model_req)
        except OSError as o:
            self.log.error(f"_get model:{o}")
            return {}
        except Exception as e:
            self.log.error(f"_get model:{e}")
        return None

    def get_model(self):
        self.log.info(f"----------------------get_model----------------------------")
        model_req = self._get_model()

        self.model = Model(model_req)
        for m in self.model.device_types:
            if m.name == "jack":
                for d in m.devices:
                    if d.is_enabled:
                        self.agvClass = "CARRIER"
                        self.model_msg["agvClass"] = self.agvClass
            elif m.name == "fork":
                for d in m.devices:
                    if d.is_enabled:
                        self.agvClass = "FORKLIFT"
                        self.model_msg["agvClass"] = self.agvClass
            elif m.name == "chassis":
                for d in m.devices:
                    if d.name == "chassis":
                        for dp in d.device_params:
                            if dp.key == "mode":
                                self.mode = dp.combo_param.child_key
                                self.model_msg["agvClass"] = self.agvClass
                            elif dp.key == "shape":
                                if dp.combo_param.child_key == "rectangle":
                                    for c_p in dp.combo_param.child_params:
                                        if c_p.key == "rectangle":
                                            for cpp in c_p.params:
                                                if cpp.key == "width":
                                                    self.width = cpp.double_value
                                                elif cpp.key == "head":
                                                    self.length += cpp.double_value
                                                elif cpp.key == "tail":
                                                    self.length += cpp.double_value
                                                elif cpp.key == "height":
                                                    self.height = cpp.double_value
                                if dp.combo_param.child_key == "circle":
                                    for c_p in dp.combo_param.child_params:
                                        if c_p.key == "circle":
                                            for cpp in c_p.params:
                                                if cpp.key == "radius":
                                                    self.width = cpp.double_value
                                                    self.length = cpp.double_value
                                                elif cpp.key == "height":
                                                    self.height = cpp.double_value

            elif m.name == "pgv":
                for d in m.devices:
                    if d.name == "chassis":
                        for dp in d.device_params:
                            if dp.key == "func":
                                self.pgv_func = dp.combo_param.child_key


class RobotMap:
    def __init__(self, rbk):
        self.edge_list = []  # 所有的高级点
        self.node_list = []  # 所有点的连线
        self.XYDir = {}  # {坐标：站点}
        self.advanced_point_list = {}  # {站点：坐标}
        self.map_dir = os.path.join("/usr/local/SeerRobotics/vda/", "robotMap")
        if not os.path.exists(self.map_dir):
            os.makedirs(self.map_dir)
        self.model_path = os.path.join(os.path.join("/usr/local/SeerRobotics/vda/", "robotMap"), "robot.smap")
        if os.path.exists(self.model_path):
            self.set_map()
        self.rbk = rbk
        self.map = None
        self.log = MyLogger()
        self.current_map = ""
        self.current_map_md5 = None

    def _get_map(self, name):
        try:

            data = self.rbk.call_service(ApiReq.ROBOT_CONFIG_DOWNLOADMAP_REQ.value, {"map_name": name})
            data_json = json.loads(data)
            if "ret_code" in data_json:
                self.log.error(f"[map]req error,{data_json}")
                return {}
            self.log.info(f"[map]map_req len :{len(data)}")
            # print(self.model_path)
            # 将模型文件写入硬盘
            with open(self.model_path, 'wb') as file:
                # 可选：写入内容到文件
                file.write(data)
                self.log.info(f"[map] _get_map OK!")
            # 解析模型文件
            return data_json
        except OSError as o:
            self.log.error(f"_get model:{o}")
            return {}
        except Exception as e:
            self.log.error(f"_get model:{e}")
        return None

    def get_map(self, name=None):
        if name:
            self.current_map = name
        self.log.info(f"----------------------get_map----------------------------")
        if self._get_current_map():
            map_req = self._get_map(self.current_map)
            if map_req:
                self.set_map(map_req)

    def set_map(self, map_req=None):
        if map_req:
            self.map = Map2D(map_req)
        else:
            with open(self.model_path, "r") as f:
                map_data = json.load(f)
                self.map = Map2D(map_data)
        if self.map:
            self.advanced_point_list = {
                str(point.instance_name): {
                    "x": point.pos.x,
                    "y": point.pos.y,
                    "z": point.pos.z,
                    "dir": point.dir
                } for point in self.map.advanced_point_list
            }
            for point in self.map.advanced_point_list:
                self.XYDir[(point.pos.x, point.pos.y, point.dir)] = point.instance_name
            self.node_list = [instance.instance_name for instance in self.map.advanced_point_list]
            self.edge_list = [(acl.start_pos.instance_name, acl.end_pos.instance_name) for acl in
                              self.map.advanced_curve_list]
        else:
            self.log.error(f'[map] no map')

    def _get_current_map(self):
        try:
            data = self.rbk.call_service(ApiReq.ROBOT_STATUS_MAP_REQ.value)
            data_json = json.loads(data)
            if data_json.get("ret_code", None):
                self.log.error("[map]req ROBOT_STATUS_MAP_REQ error")
                return ""
            self.log.info(f"[map]map_req{data_json}")
            self.current_map = data_json.get("current_map", "")
            return self.current_map
        except OSError as o:
            self.log.error(f"[map]_get_current_map:{o}")
            return ""
        except Exception as e:
            self.log.error(f"[map]_get_current_map error:{e}")
            return ""
