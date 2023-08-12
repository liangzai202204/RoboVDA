import asyncio
import configparser
import json
import os
import queue
import socket
import threading
from datetime import datetime

from rbklib.rbklib import Rbklib
from type import state
from typing import List
import time
from serve.pushMsgType import RobotPush


def get_robot_ip():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), 'config.ini')
    # 读取配置文件
    print(os.getcwd())
    print(config_path)
    config.read(config_path)
    ip = config.get('robot', 'robot_ip')
    print("robot ip:", ip)
    return ip


Robot_ip = get_robot_ip()

rbk = Rbklib(Robot_ip, push_flag=True)


class RobotMapManager:
    def __init__(self, logs):
        self.map_dir = os.path.join(os.getcwd(), "robotMap")
        self.maps = {}
        self.current_map = None
        self.current_map_md5 = None
        self.rbk = rbk
        self.logs = logs
        self.map_point_index = None
        self.get_all_map()

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
        print(f"path:{self.maps.get(map_name).get('path')}")
        return self.maps.get(map_name).get('path')

    def reload_map(self, map_dir, name, md5):
        # 在这里添加重新加载地图的逻辑
        self.load_map(map_dir, name, md5)

    def load_map(self, map_dir, name, md5=None):
        if not md5:
            md5 = self.get_updated_md5(name + '.smap')
        map_path = os.path.join(map_dir, name + '.smap')
        _, data = self.rbk.robot_config_downloadmap_req(name)
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
            _, c_md5_res = self.rbk.robot_status_mapmd5_req([map_name])
            c_md5_json = json.loads(c_md5_res)
            if c_md5_json.get("ret_code") == 0:
                if c_md5_json["map_info"][0]["name"] == map_name:
                    md5_map = c_md5_json["map_info"][0]["md5"]
                    return md5_map
                else:
                    print("獲取地圖md5時，返回的地圖名稱不相等")
            else:
                print(f"獲取地圖md5時,返回異常，{c_md5_json}")
        except KeyError as k:
            print(f"get_updated_md5{k}")
        except socket.timeout as s:
            print(f"get_updated_md5{s}")
        except Exception as e:
            print(f"get_updated_md5{e}")

    def switch_map(self, target_map: str) -> bool:
        _, map_res = self.rbk.robot_control_loadmap_req(target_map)
        map_res_json = json.loads(map_res)
        if map_res_json.get("ret_code"):
            if map_res_json["ret_code"] == 0:
                self.rbk.robot_control_reloc_req()
                return True
            else:
                return False
        return False

    def get_current_map(self,current_map=None,md5=None):
        if not os.path.exists(self.map_dir):
            os.makedirs(self.map_dir)
        if not current_map:
            self.load_map(self.map_dir,self.current_map,self.current_map_md5)
        else:
            self.load_map(self.map_dir,current_map)
            self.current_map = current_map
            self.current_map_md5 = md5
        self.map_point_index = self.map_index(self.get_map_path(self.current_map))

    def _get_map(self):
        try:
            _, map_req = self.rbk.robot_status_map_req()
            map_req_json = json.loads(map_req)
            return map_req_json
        except OSError as o:
            print("_get_map", o)

        except Exception as e:
            print("_get_map c", e)
        return None

    def get_all_map(self):
        self.logs.info(f"-----------------get_all_map---------------------")
        # 檢查是否有地圖文件

        if not os.path.exists(self.map_dir):
            # 创建目录
            os.makedirs(self.map_dir)
        map_req = self._get_map()
        map_list = map_req["maps"]
        print(map_list)
        for m in map_list:
            self.load_map(self.map_dir, m)
        # file_path = os.path.join(self.map_dir, ".smap")
        # if os.path.isfile(file_path):
        #     files = os.listdir(self.map_dir)
        #     file_names = []  # 保存文件名的列表
        #     for file in files:
        #         # 添加文件名到列表
        #         file_names.append(file)
        #         # 构造文件的完整路径
        #         file_path = os.path.join(self.map_dir, file)
        #         if os.path.isfile(file_path):
        #             with open(file_path, "r") as f:
        #                 # 读取文件内容
        #                 content = json.load(f)
        #                 print(f"文件 {file} 的内容:")
        #                 print(content)
        #                 print("---")
        #     print("文件名列表:", file_names)
        # 獲取地圖的 md5

        # 檢查是否需要更新地圖

    def map_index(self, maps: str):
        index = dict()
        nodes = dict()
        if maps == "":
            return index
        if os.path.exists(maps):
            try:
                with open(maps, "r", encoding="utf-8") as f:
                    map_data = json.load(f)
                # print(map_data)
                for node in map_data['advancedPointList']:
                    nodes[node['instanceName']] = node["pos"]

                for key, value in nodes.items():
                    index[(value["x"], value["y"])] = key
                self.logs.info(f"[map]map_index:{index}")
            except Exception as e:
                print("map_index", e)
        else:
            self.logs.error(f" no exists map :{maps}")
        return index


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"{func.__name__} start init")
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} start {(end - start) / 60:.6f}min")
        return result

    return wrapper


@timeit
class Robot:

    def __init__(self, logs):
        self.rbk = rbk
        self.task_status: asyncio.Queue[dict] = asyncio.Queue()
        self.ApiReq_queue: asyncio.Queue[ApiReq] = asyncio.Queue()
        self.map_manager = RobotMapManager(logs)
        self.logs = logs
        self.robot_push_msg = RobotPush

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
        self.online = self.robot_online
        self.robot_version = "3.4.5"
        self.messages = queue.Queue()

    def run(self):
        self.lock_robot()
        self._run()

    def _run(self):
        # self.map_manager.start_map_checking()
        while True:
            # self.try_lock_robot()
            self.get_robot_massage()

    @property
    def robot_online(self):
        """
        check robot online status,and check robot lock status
        :return:
        """
        return self.check_online()

    def update(self):
        """
        将机器人的数据，更新到 self.state 中
        :return:
        """
        self.robot_push_msg = RobotPush(**json.loads(self.rbk.pushData.get()))
        # state
        self.update_state()
        # 根據信息判斷邏輯
        # 控制權
        self.update_lock()
        # 當前地圖
        self.update_map()
        # 定位信息

    def update_state(self):
        self.state.headerId += 1
        self.state.timestamp = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
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
        self.state.driving = True if self.robot_push_msg.task_status == 2 else False
        self.state.waitingForInteractionZoneRelease = False  # TODO
        self.state.velocity = state.Velocity(vx=self.robot_push_msg.vx,
                                             vy=self.robot_push_msg.vy,
                                             omega=self.robot_push_msg.w)
        # 更新 errorseer

        self.state.errors = self.update_errors()

    def update_operating_mode(self) -> state.OperatingMode:
        mode = state.OperatingMode.MANUAL
        if self.online and self.lock:
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
        if self.robot_push_msg.current_map != self.map_manager.current_map or \
                self.robot_push_msg.current_map_md5 != self.map_manager.current_map_md5:
            self.logs.info(f"[map]current_map:{self.robot_push_msg.current_map}||{self.map_manager.current_map}"
                           f"current_map_md5:{self.robot_push_msg.current_map_md5}||{self.map_manager.current_map_md5}")
            self.map_manager.get_current_map(self.robot_push_msg.current_map,self.robot_push_msg.current_map_md5)

    def lock_robot(self):
        if self.robot_online:
            self.rbk.robot_config_lock_req(self.nick_name)
            self.lock = True
            self.logs.info("master has lock")

    def check_online(self):
        if not self.rbk.so_19204:
            self.online = False
        else:
            self.online = True

        return self.online

    def get_robot_massage(self):
        if self.robot_online:
            try:
                self.update()

            except Exception as e:
                self.logs.info(f"[robot][map]get_robot_massage error {e}")

    def send_order(self, task_list, type_id=3066):
        if not isinstance(task_list, list):
            self.logs.error("send_order is empty:", task_list)
            return
        move_task_list = {
            'move_task_list': task_list
        }
        flag = True
        try:
            while flag:
                if self.lock:
                    _, res_data = self.rbk.request(type_id, msg=move_task_list)
                    res_data_json = json.loads(res_data)
                    self.logs.info(f"下发任务内容：{move_task_list}, rbk 返回结果：{res_data_json}")
                    if res_data_json["ret_code"] == 0:
                        self.logs.info(f"下发任务成功：{move_task_list}")
                        flag = False
                    else:
                        self.logs.info(f"下发任务失败：{move_task_list}")

                else:
                    self.logs.info("没有控制权，无法下发任务")
        except Exception.args as e:
            self.logs.info("试图抢占控制权并下发任务失败，可能是没有链接到机器人" + e)

    def instant_stop_pause(self):
        send = True
        while send:
            if self.robot_online and self.lock:
                _, res = self.robot.rbk.robot_task_pause_req()
                res_json = json.loads(res)
                if "ret_code" in res_json:
                    if res_json["res_json"] == 0:
                        send = False
            else:
                self.lock_robot()

    def instant_start_pause(self):
        send = True
        while send:
            if self.robot_online and self.lock:
                _, res = self.robot.rbk.robot_task_resume_req()
                res_json = json.loads(res)
                if "ret_code" in res_json:
                    if res_json["res_json"] == 0:
                        send = False
            else:
                self.lock_robot()

    def instant_cancel_task(self):
        send = True
        while send:
            if self.robot_online and self.lock:
                self.rbk.robot_task_cancel_req()
            else:
                self.lock_robot()


class ApiReq:
    def __init__(self, api: int, req=None):
        self.api = api
        self.req = req

    def to_json(self):
        return json.dumps({"api": self.api, "req": self.req})

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(data["api"], data["req"])
