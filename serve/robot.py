import asyncio
import json
import os
import queue
import socket
import datetime

import rbklib.rbklibPro
from serve.topicQueue import TopicQueue
from type.VDA5050 import state
from typing import List
from type.pushMsgType import RobotPush
from type.ApiReq import ApiReq
from log.log import MyLogger
from parse_protobuf.Model import Model
from parse_protobuf.Map2D import Map2D


class Robot:

    def __init__(self, rbk: rbklib.rbklibPro.Rbk):
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
        # todo
        # 機器人掉綫后，仍處於在綫狀態
        # 第一次啓動時，如果機器人不在綫，地圖管理的rbk會有問題，這期間機器人上綫，不會拿到鏈接，無法更新地圖
        self.state = state.State.create_state()
        self.nick_name = "seer-vda5050"
        self.lock = False
        self.robot_version = "3.4.5"
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
                    self.init = True
                # self.logs.info(f'[robot]online status:{self.rbk.online_status}')

    @property
    def robot_online(self) -> bool:
        """
        check robot online status,and check robot lock status
        :return:
        """
        if self.rbk.online:
            return True
        self.lock = False
        return False

    async def update(self):
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
            self.logs.error(f"json.loads(push_data)：{e}")

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
                                                   localizationScore=0.,
                                                   mapDescription="")
        # 机器人名称、rbk版本
        self.state.serialNumber = self.robot_push_msg.vehicle_id
        self.state.version = self.robot_version
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
        load_goods.loadId = ""
        load_goods.loadType = goods.name
        load_goods.loadPosition = str(json.dumps(goods.point))
        return load_goods

    def update_operating_mode(self) -> state.OperatingMode:
        mode = state.OperatingMode.MANUAL
        if self.robot_online and self.lock:
            mode = state.OperatingMode.AUTOMATIC
        if not self.lock:
            mode = state.OperatingMode.SERVICE
        return mode

    def update_errors(self) -> List[state.Error]:
        def err(ers: list, e_list: list, level):
            errs = e_list
            for er in ers:
                f_child = state.Error.create_error()
                for key, value in er.items():
                    if key not in ["desc", "times"]:
                        f_child.errorType = key
                    if key in ["desc"]:
                        f_child.errorDescription = value
                    f_child.errorLevel = level
                errs.append(f_child)

        err_list = []
        if self.robot_push_msg.fatals:
            err(self.robot_push_msg.fatals, err_list, state.ErrorLevel.FATAL)
        if self.robot_push_msg.errors:
            err(self.robot_push_msg.errors, err_list, state.ErrorLevel.FATAL)
        if self.robot_push_msg.warnings:
            err(self.robot_push_msg.warnings, err_list, state.ErrorLevel.WARNING)
        if self.robot_push_msg.notices:
            err(self.robot_push_msg.notices, err_list, state.ErrorLevel.WARNING)
        return err_list

    def update_lock(self):
        if self.robot_push_msg.current_lock.nick_name == self.nick_name:
            self.lock = True
            return
        else:
            if not self.robot_push_msg.current_lock.locked:
                self.lock_robot()
                self.lock = True
            else:
                self.lock = False

    def update_map(self):
        if not self.map.current_map_md5:
            self.map.current_map_md5 = self.robot_push_msg.current_map_md5
        if self.robot_push_msg.current_map != self.map.current_map or self.map.current_map_md5 != self.robot_push_msg.current_map_md5:
            self.logs.info(f"[map]current_map:{self.robot_push_msg.current_map}||{self.map.current_map}"
                           f"current_map_md5:{self.robot_push_msg.current_map_md5}||")
            self.map.get_map(self.robot_push_msg.current_map)

    def lock_robot(self):
        if self.robot_online:
            # self.rbk.robot_config_lock_req(self.nick_name)
            self.rbk.call_service(ApiReq.ROBOT_CONFIG_LOCK_REQ.value, {"nick_name": self.nick_name})
            self.lock = True
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
                if self.lock:
                    # res_data = self.rbk.request(3066, msg=move_task_list)
                    res_data = self.rbk.call_service(ApiReq.ROBOT_TASK_GOTARGETLIST_REQ.value, move_task_list)
                    res_data_json = json.loads(res_data)
                    self.logs.info(f"下发任务内容：{move_task_list}, rbk 返回结果：{res_data_json}")
                    if res_data_json["ret_code"] == 0:
                        self.logs.info(f"下发任务成功：{move_task_list}")
                        flag = False
                    else:
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
                if self.robot_online and self.lock:
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


class RobotMapManager:
    def __init__(self, rbk):
        self.map_dir = os.path.join(os.getcwd(), "robotMap")
        self.maps = {}
        self.current_map = None
        self.current_map_md5 = None
        self.rbk = rbk
        self.logs = MyLogger()
        self.map_point_index = None

    def add_map(self, map_name, md5, map_path):
        self.maps[map_name] = {
            'md5': md5,
            'path': map_path
        }

    def remove_map(self, map_name):
        if map_name in self.maps:
            try:
                os.remove(self.maps[map_name]['path'])
                self.logs.info(f"del map file:{self.maps[map_name]['path']}")
                del self.maps[map_name]
            except OSError as e:
                self.logs.info(f"Error deleting file {map_name}: {str(e)}")
        if self.current_map == map_name:
            self.current_map = None
            self.map_point_index = None

    def get_md5(self, map_name):
        return self.maps.get(map_name).get('md5')

    def get_map_path(self, map_name):
        self.logs.info(f"path:{self.maps.get(map_name).get('path')}")
        return self.maps.get(map_name).get('path')

    def reload_map(self, map_dir, name, md5):
        # 在这里添加重新加载地图的逻辑
        self.load_map(map_dir, name, md5)

    def load_map(self, map_dir, name, md5=None):
        if not md5:
            md5 = self.get_updated_md5(name + '.smap')
        map_path = os.path.join(map_dir, name + '.smap')
        # data = self.rbk.robot_config_download_map_req(name)
        data = self.rbk.call_service(ApiReq.ROBOT_CONFIG_DOWNLOADMAP_REQ.value, {"map_name": name})
        if os.path.exists(map_dir):
            with open(map_path, 'wb') as file:
                # 可选：写入内容到文件
                file.write(data)
            self.logs.info(f"[robot] load map OK! map name:{name},save path:{map_path}")
            self.add_map(name, md5, map_path)
        else:
            self.logs.error(f"[robot] try to get robot map,but state has no {map_dir}"
                            f",path:{map_path}")

    def get_updated_md5(self, map_name: str):
        try:
            # c_md5_res = self.rbk.robot_status_map_md5_req([map_name])
            c_md5_res = self.rbk.call_service(ApiReq.ROBOT_STATUS_MAPMD5_REQ.value, {"map_names": [map_name]})
            c_md5_json = json.loads(c_md5_res)
            if c_md5_json.get("ret_code") == 0:
                if c_md5_json["map_info"][0]["name"] == map_name:
                    md5_map = c_md5_json["map_info"][0]["md5"]
                    return md5_map
                else:
                    self.logs.error(f"[map]獲取地圖md5時，返回的地圖名稱不相等")
            else:
                self.logs.error(f"[map]獲取地圖md5時,返回異常，{c_md5_json}")
        except KeyError as k:
            self.logs.error(f"[map]get_updated_md5{k}")
        except socket.timeout as s:
            self.logs.error(f"[map]get_updated_md5{s}")
        except Exception as e:
            self.logs.error(f"[map]get_updated_md5{e}")

    def switch_map(self, target_map: str) -> bool:
        # map_res = self.rbk.robot_control_load_map_req(target_map)
        map_res = self.rbk.call_service(ApiReq.ROBOT_CONTROL_LOADMAP_REQ.value, {"map_name": target_map})
        map_res_json = json.loads(map_res)
        if map_res_json.get("ret_code"):
            if map_res_json["ret_code"] == 0:
                # self.rbk.robot_control_reloc_req()
                self.rbk.call_service(ApiReq.ROBOT_CONTROL_RELOC_REQ.value)
                return True
            else:
                return False
        return False

    def get_current_map(self, current_map=None, md5=None):
        if not os.path.exists(self.map_dir):
            os.makedirs(self.map_dir)
        if not current_map:
            self.load_map(self.map_dir, self.current_map, self.current_map_md5)
        else:
            self.load_map(self.map_dir, current_map)
            self.current_map = current_map
            self.current_map_md5 = md5
        self.map_point_index = self.map_index(self.get_map_path(self.current_map))

    def _get_map(self):
        try:
            map_req = self.rbk.call_service(ApiReq.ROBOT_STATUS_MAP_REQ.value)
            if not map_req:
                self.logs.error("[map]req error")
                return {}
            self.logs.info(f"[map]map_req{map_req}")
            map_req_json = json.loads(map_req)
            return map_req_json
        except OSError as o:
            self.logs.error(f"_get_map:{o}")
            return {}
        except Exception as e:
            self.logs.error(f"[map]_get_map error:{e}")
        return None

    def get_all_map(self):
        self.logs.info(f"-----------------get_all_map---------------------")
        # 檢查是否有地圖文件

        if not os.path.exists(self.map_dir):
            # 创建目录
            os.makedirs(self.map_dir)
        map_req = self._get_map()
        map_list = map_req.get("maps")
        if not map_list:
            self.logs.error(f"[map]加載失敗")
            return
        self.logs.info(f"map_list:{map_list}")
        for m in map_list:
            self.load_map(self.map_dir, m)

    def map_index(self, maps: str):
        index = dict()
        nodes = dict()
        if maps == "":
            return index
        if os.path.exists(maps):
            try:
                with open(maps, "r", encoding="utf-8") as f:
                    map_data = json.load(f)
                for node in map_data['advancedPointList']:
                    nodes[node['instanceName']] = node["pos"]

                for key, value in nodes.items():
                    index[(value["x"], value["y"])] = key
                self.map_point_index = index
                self.logs.info(f"[map]map_index:{index}")
            except Exception as e:
                self.logs.error(f"[map]map_index{e}")
        else:
            self.logs.error(f"[map]no exists map :{maps}")
        return index


class RobotModel:
    def __init__(self, rbk):
        self.model_dir = os.path.join(os.getcwd(), "robotModel")
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        self.model_path = os.path.join(os.path.join(os.getcwd(), "robotModel"), "robot.model")
        self.rbk = rbk
        self.model = None
        self.log = MyLogger()

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
            print(m.name)
            if m.name == "chassis":
                for d in m.devices:
                    for dp in d.device_params:
                        if dp.key == "mode":
                            print("mode",dp.combo_param.child_key)


class RobotMap:
    def __init__(self, rbk):
        self.advanced_point_list = []
        self.map_dir = os.path.join(os.getcwd(), "robotMap")
        if not os.path.exists(self.map_dir):
            os.makedirs(self.map_dir)
        self.model_path = os.path.join(os.path.join(os.getcwd(), "robotMap"), "robot.smap")
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
                self.map = Map2D(map_req)
                self.advanced_point_list = [point.class_name for point in self.map.advanced_point_list]

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
