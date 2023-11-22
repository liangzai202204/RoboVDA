import json
import math
import os
import socket
import struct
import threading
import time
from datetime import datetime
from queue import Queue

PACK_FMT_STR = '!BBHLH6s'


def rbk_lock_decorator(func):
    # 创建锁对象
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        # 获取锁
        with lock:
            # 在加锁范围内执行方法
            return func(*args, **kwargs)

    # 返回装饰后的方法
    return wrapper


class Rbklib:
    def __init__(self, ip, core_flag=False, push_flag=False, pushDataSize: int = 1) -> None:
        self.rbk_lock = threading.Lock()
        self.ip = ip
        try:
            # 机器人状态 socket
            self.so_19204 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.so_19204.mutex = threading.Lock()
            self.so_19204.connect((self.ip, 19204))
            self.so_19204.settimeout(60)
        except:
            self.so_19204 = None
        print("core_flag", core_flag)
        if core_flag == False:
            try:
                # 机器人控制 socket
                self.so_19205 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # self.so_19205.mutex = threading.Lock()
                self.so_19205.connect((self.ip, 19205))
                self.so_19205.settimeout(60)
            except:
                self.so_19205 = None
            try:
                # 机器人导航 socket
                self.so_19206 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # self.so_19206.mutex = threading.Lock()
                self.so_19206.connect((self.ip, 19206))
                self.so_19206.settimeout(60)
            except:
                self.so_19206 = None
        else:
            self.so_19205 = None
            self.so_19206 = None
        try:
            # 机器人配置 socket
            self.so_19207 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.so_19207.mutex = threading.Lock()
            self.so_19207.connect((self.ip, 19207))
            self.so_19207.settimeout(60)
        except:
            self.so_19207 = None
        try:
            # 其他 socket
            self.so_19210 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.so_19210.mutex = threading.Lock()
            self.so_19210.connect((self.ip, 19210))
            self.so_19210.settimeout(60)
        except:
            self.so_19210 = None
        # 机器人推送 socket
        if push_flag:
            self.so_19301 = socket.socket()
            self.so_19301.connect((self.ip, 19301))
            self.pushThreadFlag = True
            self.pushData = Queue(pushDataSize)
            thread = threading.Thread(target=self._robot_push)
            thread.setDaemon(True)
            thread.start()

    def __del__(self):
        if self.so_19204 != None:
            self.so_19204.close()
        if self.so_19205 != None:
            self.so_19205.close()
        if self.so_19206 != None:
            self.so_19206.close()
        if self.so_19207 != None:
            self.so_19207.close()
        if self.so_19210 != None:
            self.so_19210.close()

    def request(self, msgType, reqId=1, msg=None,sock=None):
        """
        发送请求

        :param msgType: 报文类型
        :param reqId: 序号
        :param msg: 消息体/数据区
        :param so:  使用指定的socket
        :return: 响应，包含报文头和报文体的元组，报文头[2：序号 3：报文体长度 4：报文类型]
        """
        with self.rbk_lock:
            if sock:
                # 如果指定了socket，则使用指定的socket,否则使用报文类型对应的socket
                so = sock
            elif 1000 <= msgType < 2000:
                so = self.so_19204
            elif msgType < 3000:
                so = self.so_19205
            elif msgType < 4000:
                so = self.so_19206
            elif msgType < 5000:
                so = self.so_19207
            elif 6000 <= msgType < 7000:
                so = self.so_19210
            else:
                # 如果报文类型不在范围内，则抛出异常
                raise ValueError("没有与报文类型对应的socket,或者需要指定一个socket")
            ################################################################################################################
            # 打印socket信息
            # print("*" * 20, "socket信息", "*" * 20)
            # print(f"{'socket:':>10}\tserver{so.getpeername()},local{so.getsockname()}")
            # print()
            ################################################################################################################
            # 封装报文
            if msg is not None:
                # 如果报文体不为空，则使用报文体
                if isinstance(msg, (dict, list)):
                    # 如果报文体是dict或者list，则转换成字节
                    body = bytearray(json.dumps(msg), "ascii")
                else:
                    # 如果报文体是bytes或者bytearray，则直接使用
                    body = msg
                msgLen = len(body)
            else:
                msgLen = 0
            rawMsg = struct.pack(PACK_FMT_STR, 0x5A, 0x01, reqId, msgLen, msgType, b'\x00\x00\x00\x00\x00\x00')
            ################################################################################################################
            # 打印请求报文信息
            # print("*" * 20, "请求信息", "*" * 20)
            # print(f"{'时间:':　>6}\t", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), sep='')
            # print(f"{'报文类型:':　>6}\t{msgType}\t{msgType:#06X}")
            # print(f"{'序号:':　>6}\t{reqId}\t{reqId:#06X}")
            # print(f"{'报文头:':　>6}\t{rawMsg.hex(' ').upper()}")
            # print(f"{'报文体长度:':　>6}\t{msgLen}\t{msgLen:#010X}")
            # if msgLen == 0:
            #     print(f"{'报文体:':　>6}\t无")
            # else:
            #     print(f"{'报文体:':　>6}\t{body[:1000]}")
            #     if msgLen > 1000:
            #         print("...")
            # print()
            ################################################################################################################
            # 发送报文
            if msgLen > 0:
                rawMsg += body
            # so.mutex.acquire()
            so.sendall(rawMsg)
            # 接收报文头
            headData = so.recv(16)
            # 解析报文头
            header = struct.unpack(PACK_FMT_STR, headData)
            # 获取报文体长度
            bodyLen = header[3]
            readSize = 1024
            recvData = b''
            while (bodyLen > 0):
                recv = so.recv(readSize)
                recvData += recv
                bodyLen -= len(recv)
                if bodyLen < readSize:
                    readSize = bodyLen
            data = recvData[:header[3]]
            # so.mutex.release()
            ################################################################################################################
            # # 打印响应报文信息
            # print("*" * 20, "响应信息", "*" * 20)
            # print(f"{'时间:':　>6}\t", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), sep='')
            # print(f"{'报文类型:':　>6}\t{header[4]}\t{header[4]:#06X}")
            # print(f"{'序号:':　>6}\t{header[2]}\t{header[2]:#06X}")
            # print(f"{'报文头:':　>6}\t{headData.hex(' ').upper()}")
            # print(f"{'报文体长度:':　>6}\t{header[3]}\t{header[3]:#010X}")
            # print(f"{'报文体:':　>6}\t{data[:1000]}")
            # if header[3] > 1000:
            #     print("...")
            # print()
            ################################################################################################################
        return header, data

    # 以下是查询机器人状态API
    # 机器人状态 API 用于查询机器人的所有状态量。

    def robot_status_info_req(self):
        """
        查询机器人信息
        """
        return self.request(1000)

    def robot_status_run_req(self):
        """
        查询机器人的运行状态信息(如运行时间、里程等)
        """
        return self.request(1002)

    def robot_status_loc_req(self):
        """
        查询机器人在世界坐标系中的坐标
        """
        return self.request(1004)

    def robot_status_speed_req(self):
        """
        查询机器人速度
        """
        return self.request(1005)

    def robot_status_block_req(self):
        """
        查询机器人的被阻挡状态
        """
        return self.request(1006)

    def robot_status_battery_req(self, simple: bool = False):
        """
        查询机器人电池状态

        :param simple: 是否只返回简单数据, true = 是，false = 否，缺省则为否
        """
        return self.request(1007, 1, {"simple": simple})

    def robot_status_laser_req(self, return_beams3D: bool = False):
        """
        查询机器人激光点云数据

        :param return_beams3D: 是否返回多线激光数据，true = 返回，false = 不返回，缺省则为不返回
        """
        return self.request(1009, 1, {"return_beams3D": return_beams3D})

    def robot_status_path_req(self):
        """
        查询机器人自由导航路径数据\n
        注意：机器人的路径数据只有在自由导航的时候才有意义，路径导航时机器人是沿着绘制的贝塞尔曲线运动的，通过该 API 查询到的路径数据没有意义,
        如果需要查询路径导航以及巡检时的路径，使用 robot_status_task_req
        """
        return self.request(1010)

    def robot_status_area_req(self):
        """
        查询机器人当前所在的区域信息
        """
        return self.request(1011)

    def robot_status_emergency_req(self):
        """
        查询机器人急停按钮的状态
        """
        return self.request(1012)

    def robot_status_io_req(self):
        """
        查询机器人 I/O 数据
        """
        return self.request(1013)

    def robot_status_imu_req(self):
        """
        查询机器人 IMU 数据
        """
        return self.request(1014)

    def robot_status_rfid_req(self):
        """
        查询 RFID 数据
        """
        return self.request(1015)

    def robot_status_ultrasonic_req(self):
        """
        查询机器人的超声传感器数据
        """
        return self.request(1016)

    def robot_status_pgv_req(self):
        """
        查询二维码数据(PGV)数据
        """
        return self.request(1017)

    def robot_status_encoder_req(self):
        """
        查询编码器脉冲值
        """
        return self.request(1018)

    def robot_status_task_req(self, simple: bool = False):
        """
        查询机器人当前的导航状态, 导航站点, 导航相关路径(已经经过的站点, 尚未经过的站点)等
        :param simple: 是否只返回简单数据, true = 是，false = 否，缺省则为否
        """
        return self.request(1020, 1, {"simple": simple})

    def robot_status_reloc_req(self):
        """
         查询机器人当前的定位状态
        """
        return self.request(1021)

    def robot_status_loadmap_req(self):
        """
         查询机器人当前地图载入状态
        """
        return self.request(1022)

    def robot_status_slam_req(self):
        """
         查询机器人当前的扫图状态
        """
        return self.request(1025)

    def robot_status_jack_req(self):
        """
         查询顶升机构状态\n
         仅对选配顶升机构的机器人有意义\n
         推荐使用 robot_task_gotarget_req 发送顶升任务，使用 robot_status_task_req 查询任务状态
        """
        return self.request(1027)

    def robot_status_fork_req(self):
        """
         查询货叉(叉车)状态\n
         仅对有货叉的机器人有意义, 如叉车等
        """
        return self.request(1028)

    def robot_status_roller_req(self):
        """
         查询辊筒(皮带)状态\n
         仅对选配有辊筒或皮带的机器人有意义
        """
        return self.request(1029)

    def robot_status_dispatch_req(self) -> None:
        """
        查询机器人当前的调度状态\n
        弃用
        """
        # pass
        return self.request(1030)

    def robot_status_motor_req(self, motor_names=None):
        """
        查询电机状态信息

        :param motor_names: 根据电机名称查询指定电机状态信息如果缺省该字段表示查询所有电机状态信息
        """
        if motor_names:
            return self.request(1040, 1, {"motor_names": motor_names})
        return self.request(1040)

    def robot_status_alarm_req(self):
        """
        查询机器人当前的报警状态
        """
        return self.request(1050)

    def robot_status_current_lock_req(self):
        """
        查询当前控制权所有者
        """
        return self.request(1060)

    def robot_status_all1_req(self, keys=None, return_laser: bool = True,
                              return_beams3D: bool = False):
        """
        查询批量数据1\n
        all1 是为了通过一个请求批量获取之前提到的大部分状态数据, 包括 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007,
        1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1019, 1020, 1021, 1022, 1025, 1027, 1028,
        1029, 1030, 1050等

        :param keys: 只返回数组中指定的 key-value，缺省则为返回所有数据
        :param return_laser: 是否返回激光数据（即1009的数据），true = 返回，false = 不返回，缺省则为返回
        :param return_beams3D: 是否返回多线激光数据（即1009中多线的数据），true = 返回，false = 不返回，缺省则为不返回
        """
        d = {}
        if keys:
            d["keys"] = keys
        d["return_laser"] = return_laser
        d["return_beams3D"] = return_beams3D
        return self.request(1100, 1, d)

    def robot_status_all2_req(self, return_laser: bool = True):
        """
        查询批量数据2\n
        all2 是为了通过一个请求批量获取更新比较频繁或比较实时的数据(如位置, 速度等), 包括 1004, 1005, 1006, 1009, 1010,
        1011, 1012, 1013, 1014, 1016, 1017, 1020, 1050

        :param return_laser: 是否返回激光数据（即1009的数据），true = 返回，false = 不返回，缺省则为返回
        """
        return self.request(1101, 1, {"return_laser": return_laser})

    def robot_status_all3_req(self):
        """
        查询批量数据3\n
        all3 是为了通过一个请求批量获取更新不频繁的状态数据, 包括 1002, 1007, 1021, 1022, 1025
        """
        return self.request(1102)

    def robot_status_task_status_package_req(self, task_ids=None):
        """
        查询机器人任务状态

        :param task_ids: 数组中指定所需查询的任务 task_id 如果数组为空，则响应也为空；如果缺省该字段，
        则返回机器人最近已完成的一个任务状态和所有未完成的任务状态
        """
        if task_ids:
            return self.request(1110, 1, {"task_ids": task_ids})
        return self.request(1110)


    def robot_status_map_req(self):
        """
        查询机器人载入的地图以及储存的地图
        """
        return self.request(1300)

    def robot_status_station(self):
        """
        查询机器人当前载入地图中的站点信息\n
        该 API 用于获得地图中所有站点的坐标、角度以及类型信息
        """
        return self.request(1301)

    def robot_status_mapmd5_req(self, map_names):
        """
        查询指定地图列表的MD5值

        :param map_names: 需要查询的地图列表，应该保证机器人中存在地图列表中所有的地图
        """
        return self.request(1302, 1, {"map_names": map_names})

    def robot_status_params_req(self, plugin: str = "", param: str = ""):
        """
        查询机器人参数信息

        :param plugin: 参数所属的插件名, 如果缺省, 表示查询所有插件的所有参数
        :param param: 参数名, 如果 plugin 存在，但 param 缺省，代表查询该插件的所有参数。否则查询该插件的指定参数
        """
        d = {}
        if plugin:
            d["plugin"] = plugin
        if param:
            d["param"] = param
        if d:
            return self.request(1400, 1, d)
        return self.request(1400)

    def robot_status_model_req(self):
        """
        下载机器人模型文件\n
        如果不发生错误, 数据区中的内容为 json 格式的机器人模型文件
        """
        return self.request(1500)

    def robot_status_transparent_req(self):
        '''
        查询透传的数据信息
        '''
        return self.request(1900)

    def robot_status_canframe_req(self):
        """
        查询驱动器参数
        """
        return self.request(1750)

    def robot_status_gnsscheck_req(self, id: str = ""):
        """
        查询机器人 GNSS 连接状态

        :param id: GNSS id
        """
        if id:
            return self.request(1760, 1, {"id": id})
        return self.request(1760)

    def robot_status_gnsslist_req(self):
        '''
        查询机器人 GNSS 设备列表
        '''
        return self.request(1761)

    def robot_status_downloadfile_req(self, type: str = "", file_path: str = ""):
        """
        下载机器人文件

        :param type: 机器人文件的类型，“app”=机器人程序目录下的文件，“users”=机器人用户目录下的文件
        :param file_path: 机器人文件的相对路径，针对于type指定的文件类型
        """
        d = {}
        if type:
            d["type"] = type
        if file_path:
            d["file_path"] = file_path
        if d:
            return self.request(1800, 1, d)
        return self.request(1800)

    def robot_status_removefile_req(self, type: str = "", file_path: str = ""):
        """
        删除机器人文件

        :param type: 机器人文件的类型，“app”=机器人程序目录下的文件，“users”=机器人用户目录下的文件，“submaps”=机器人子地图目录下的子地图
        :param file_path: 机器人文件的相对路径，针对于type指定的文件类型
        """
        d = {}
        if type:
            d["type"] = type
        if file_path:
            d["file_path"] = file_path
        if d:
            return self.request(1801, 1, d)
        return self.request(1801)

    def robot_status_submaps_list_req(self, map_name: str):
        """
        查询机器人子地图

        :param map_name: 	需要查询子地图的母地图名字
        """
        return self.request(1802, 1, {"map_name": map_name})

    def robot_status_sound_req(self):
        return self.request(1850)

    # 以下是机器人控制API
    # 机器人控制 API 主要用于发送开环的控制指令
    #
    # 注: 确认定位确认 (2003) , 机器人载入地图状态 (1022) 为 SUCCESS, 机器人重定位状态 (1021) 为 COMPLETED 的情况下才能使用。
    # 确认成功后，重定位状态 (1021) 将会变为 SUCCESS

    def robot_control_stop_req(self):
        """
        停止开环运动
        """
        return self.request(2000)

    def robot_control_reloc_req(self, x: float = None, y: float = None, angle: float = None, length: float = 0,
                                home: bool = False):
        """
         重定位

         :param x: 世界坐标系中的 x 坐标, 单位 m
         :param y: 世界坐标系中的 y 坐标, 单位 m
         :param angle: 世界坐标系中的角度, 单位 rad
         :param length: 重定位区域半径，单位 m
         :param home: 在 RobotHome 重定位(若为 true, 前三个参数无效, 并从 Roboshop 参数配置中的 RobotHome1-5 重定位,
                      若 RobotHome1-5 未配置, 则不做任何操作。若缺省则认为是 false)
         """
        d = {}
        if x is not None:
            d["x"] = x
        if y is not None:
            d["y"] = y
        if angle is not None:
            d["angle"] = angle
        if length is not None:
            d["length"] = length
        d["home"] = home
        return self.request(2002, 1, d)

    def robot_control_comfirmloc_req(self):
        """
        确认定位正确
        """
        return self.request(2003)

    def robot_control_cancelreloc_req(self):
        """
        取消重定位\n
        用于取消重定位过程, 如果当前正在重定位(即 reloc_status = 2 时)将取消本次重定位, 机器人的定位位置将回到发送重定位指令前的位置,
        并且 reloc_status 将变为 3 (重定位完成)。 如果当前没有正在重定位, 则本条指令没有任何作用。
        """
        return self.request(2004)

    def robot_control_motion_req(self, vx: float = 0, vy: float = 0, w: float = 0, steer: float = None,
                                 reel_steer: float = None, duration: float = None):
        """
        开环运动

        :param vx: 机器人在机器人坐标系中的 x 轴方向速度, 若缺省则认为是 0, 单位 m/s
        :param vy: 机器人在机器人坐标系中的 y 轴方向速度, 若缺省则认为是 0, 单位 m/s
        :param w: 机器人在机器人坐标系中的角速度(即顺时针转为负, 逆时针转为正), 若缺省则认为是 0, 单位 rad/s
        :param steer: -2= 一键回零，1=15° 递增，-1=15° 递减（机器人坐标系），仅当单舵轮机器人时该值有效，该字段存在时，不响应 vy 和 w，
                      此时 vx 含义变为舵轮线速度
        :param reel_steer: 目标舵角值（机器人坐标系）, 单位 rad, 仅当单舵轮机器人时该值有效，该字段存在时，不响应 vy 和 w，
                           此时 vx 含义变为舵轮线速度，优先级大于 steer
        :param duration: 机器人使用开环速度运动的持续时间, 单位 ms, 0= 一直保持当前开环速度运动, 该参数缺省时，
                         使用参数配置中 ControlMotionDuration 的数值
        """
        d = {"vx": vx, "vy": vy, "w": w}
        if steer is not None:
            d["steer"] = steer
        if reel_steer is not None:
            d["reel_steer"] = reel_steer
        if duration is not None:
            d["duration"] = duration
        return self.request(2010, 1, d)

    def robot_control_loadmap_req(self, map_name: str):
        """
        切换载入的地图

        :param map_name: 要切换的地图名(不能包含中文等非法字符, 只能使用 0-9, a-z, A-Z, -, _)
        """
        return self.request(2022, 1, {"map_name": map_name})

    def robot_control_clearmotorencoder_req(self, name: str):
        """
        对指定电机标零

        :param name: 要标零的电机名
        """
        return self.request(2024, 1, {"name": name})

    def robot_config_upload_and_loadmap_req(self, file_path: str):
        '''
        上传并切换载入地图
        file_path: 上传文件的 路径+文件名字
        '''
        with open(file_path, "rb") as f:
            file = f.read()
            f.close()
        return self.request(2025, 1, file)

    # 以下是机器人导航 API
    # 机器人导航 API 主要用于发送导航相关的指令。

    def robot_task_pause_req(self):
        """
        暂停当前导航
        """
        return self.request(3001)

    def robot_task_resume_req(self):
        """
        继续当前导航
        """
        return self.request(3002)

    def robot_task_cancel_req(self):
        """
        取消当前导航
        """
        return self.request(3003)

    def robot_task_gotarget_req(self, **kwargs):
        """
        路径导航\n
        路径导航为向机器人发送一个目标站点，由机器人自动规划路径运行，经过中间站点不进行停留。

        :param kwargs: 参阅 https://books.seer-group.com/public/netprotocol/3.3/zh/dev-integration/netprotocol/tcp-ip/task-api/robot-task-gotarget.html
        """
        return self.request(3051, 1, kwargs)

    def robot_task_gotarget2_req(self, **kwargs):
        """
        路径导航\n
        路径导航为给定目标站点, 由机器人自动规划沿着贝塞尔曲线的路径运行, 期间会经过其它中间站点但不会停留。

        :param kwargs: 参阅 https://books.seer-group.com/public/netprotocol/3.3/zh/dev-integration/netprotocol/tcp-ip/task-api/robot-task-gotarget2.html
        :return:
        """
        return self.request(3052, 1, kwargs)

    def robot_task_target_path_req(self, id: str):
        """
        获取路径导航的路径

        :param id: 目标站点的 id
        """
        return self.request(3053, 1, {"id": id})

    def robot_task_translate_req(self, dist: float, vx: float = None, vy: float = None, mode: int = None):
        """
        平动，以固定速度直线运动固定距离\n
        注意: 3055(平动), 3056(转动), 3057, 3058 不能同时进行。如果 vx, vy 都有值, 则会将速度合成。 里程模式不需要定位精准,
        但是对于长距离的运动可能会产生较大误差,误差随距离的增大而增大。定位模式需要当前环境定位稳定, 误差与当前环境和定位精度相关。

        :param dist: 直线运动距离, 绝对值, 单位: m
        :param vx: 机器人坐标系下 X 方向运动的速度, 正为向前, 负为向后, 单位: m/s
        :param vy: 机器人坐标系下 Y 方向运动的速度, 正为向左, 负为向右, 单位: m/s
        :param mode: 0 = 里程模式(根据里程进行运动), 1 = 定位模式, 若缺省则默认为里程模式
        """
        d = {"dist": dist}
        if vx is not None:
            d["vx"] = vx
        if vy is not None:
            d["vy"] = vy
        if mode is not None:
            d["mode"] = mode
        return self.request(3055, 1, d)

    def robot_task_turn_req(self, angle: float, vw: float, mode: int = None):
        """
        转动, 以固定角速度旋转固定角度\n
        注意: 3055(平动), 3056(转动), 3057, 3058 不能同时进行。里程模式不需要定位精准, 但是对于角度很大的转动动可能会产生较大误差,
        误差随旋转角度的增大而增大。 定位模式需要当前环境定位稳定, 误差与当前环境和定位精度相关。

        :param angle: 转动的角度(机器人坐标系), 绝对值, 单位 rad, 可以大于 2π
        :param vw: 转动的角速度(机器人坐标系), 正为逆时针转, 负为顺时针转 单位 rad/s
        :param mode: 0 = 里程模式(根据里程进行运动), 1 = 定位模式, 若缺省则默认为里程模式
        """
        d = {"angle": angle, "vw": vw}
        if mode:
            d["mode"] = mode
        return self.request(3056, 1, d)

    def robot_task_spin_req(self, increase_spin_angle: float = None, robot_spin_angle: int = None,
                            global_spin_angle: int = None, spin_direction: int = None):
        """
        对托盘进行旋转\n
        注意: 3055(平动), 3056(转动), 3057, 3058 不能同时进行\n
        注意1: 托盘旋转所有角度都是 “弧度”制\n
        注意2: 托盘在非随动的情况下，如果顶升机构处于下降状态，机器人导航前会将自动将托盘角度归零，如果顶升机构处于顶起状态，
        机器人导航前会将自动将托盘角度就近归零或转到 180 度。可以通过将参数 AutoSpinToZeroInUnload(下降状态)，
        AutoSpinToZero（顶起状态）设置为 false 来关闭这个特性。

        :param increase_spin_angle: 在当前托盘角度基础上增加一个角度, 角度为正数则逆时针旋转, 为负数顺时针旋转
        :param robot_spin_angle: 将托盘的角度转到机器人坐标系下的一个角度。spin_direction为0, 则就近转过去; spin_direction为1,
                                 则逆时针转过去; spin_direction为-1, 则顺时针转过去
        :param global_spin_angle: 将托盘的角度转到世界坐标系下的一个角度。spin_direction为0, 则就近转过去; spin_direction为1,
                                  则逆时针转过去; spin_direction为-1, 则顺时针转过去
        :param spin_direction: 0 = 就近, 1 = 逆时针, -1=顺时针
        """
        d = {}
        if increase_spin_angle is not None:
            d["increase_spin_angle"] = increase_spin_angle
        if robot_spin_angle is not None:
            d["robot_spin_angle"] = robot_spin_angle
        if global_spin_angle is not None:
            d["global_spin_angle"] = global_spin_angle
        if spin_direction is not None:
            d["spin_direction"] = spin_direction
        if d:
            return self.request(3057, 1, d)
        return self.request(3057)

    def robot_task_circular_req(self, rot_radius: float = None, rot_degree: float = None,
                                rot_speed: float = None, mode: int = None):
        """
        圆弧运动\n
        注意: 3055(平动), 3056(转动), 3057, 3058 不能同时进行

        :param rot_radius: 旋转半径, 单位m; 圆心在机器人坐标系左边为正, 右边为负
        :param rot_degree: 旋转角度, 单位度
        :param rot_speed: 旋转速度, 单位为 rad/s, 如果是负数, 则说明是顺时针走
        :param mode: 0 = 里程模式(根据里程进行运动), 1 = 定位模式, 若缺省则默认为里程模式
        """
        d = {}
        if rot_radius is not None:
            d["rot_radius"] = rot_radius
        if rot_degree is not None:
            d["rot_degree"] = rot_degree
        if rot_speed is not None:
            d["rot_speed"] = rot_speed
        if mode is not None:
            d["mode"] = rot_speed
        if d:
            return self.request(3058, 1, d)
        return self.request(3058)

    def robot_task_gotargetlist_req(self, **kwargs):
        """
        指定路径导航\n
        指定路径导航为向机器人发送一组站点序列，机器人会按照此序列进行导航（不再自主规划路径），经过中间站点不进行停留。

        :param kwargs: 参阅 https://books.seer-group.com/public/netprotocol/3.3/zh/dev-integration/netprotocol/tcp-ip/task-api/robot-task-gotargetlist.html
        """
        return self.request(3066, 1, kwargs)

    def robot_task_cleartargetlist_req(self):
        """
        清除指定导航路径\n
        清除指定路径导航 [3066]robot_task_gotargetlist_req 所下发的站点序列，机器人将停止运动
        """
        return self.request(3067)

    def robot_tasklist_status_req(self, with_robot_status: bool = None, task_list_name: str = None):
        d = {}
        if with_robot_status is not None:
            d["with_robot_status"] = with_robot_status
        if task_list_name is not None:
            d["task_list_name"] = task_list_name
        if d:
            return self.request(3101, 1, d)
        return self.request(3101)

    def robot_tasklist_name_req(self, name: str):
        """
        执行预存任务链

        :param name: 预存的任务链的名称(使用 Roboshop 上传)
        """
        return self.request(3106, 1, {"name": name})

    def robot_tasklist_req(self, **kwargs):
        """
        执行发送任务链
        """
        return self.request(3100, 1, kwargs)

    def robot_tasklist_cancel_req(self):
        """
        取消正在执行的任务链
        """
        return self.request(3104)

    # 以下是机器人配置 API
    # 机器人配置 API 用于配置机器人、切换地图等。

    def robot_config_require_req(self):
        """
        回收控制权\n
        从调度系统回收控制权。 回收控制权后，如果当前有任何导航正在进行，都将被取消。
        """
        return self.request(4001)

    def robot_config_release_req(self):
        """
        释放控制权\n
        释放控制权给调度系统, 只有定位状态正确的时候才能释放。当成功释放控制权给调度系统后, 机器人将不响应除状态查询外的任何指令。
        释放控制权后，如果当前有任何导航正在进行，都将被取消。
        """
        return self.request(4002)

    def robot_config_src_require_req(self):
        """
        SRC 控制模式\n
        将 SRC 设置为控制模式，此时不能有其他控制器控制机器人
        """
        return self.request(4003)

    def robot_config_src_release_req(self):
        """
        SRC 监听模式\n
        将 SRC 设置为监听模式，让机器人通过其他控制器控制
        """
        return self.request(4004)

    def robot_config_lock_req(self, nick_name: str):
        """
        抢占控制权
        :param nick_name: 控制权抢占者名称
        """
        return self.request(4005, 1, {"nick_name": nick_name})

    def robot_config_unlock_req(self):
        """
        释放控制权\n
        只能释放自己抢占的控制权，不能释放别人的控制权，如果想取得控制权，须抢占
        """
        return self.request(4006)

    def robot_config_clearallerrors_req(self):
        """
        清除机器人当前所有报错
        """
        return self.request(4009)

    def robot_config_uploadmap_req(self, mapPath: str):
        """
        上传地图到机器人

        :param mapPath: 地图文件路径
        """
        with open(mapPath, "rb") as f:
            d = f.read()
        return self.request(4010, 1, d)

    def robot_config_downloadmap_req(self, map_name: str):
        """
        从机器人下载地图

        :param map_name: 地图名(不能包含中文等非法字符, 只能使用 0-9, a-z, A-Z, -, _)
        """
        return self.request(4011, 1, {"map_name": map_name})

    def robot_config_removemap_req(self, map_name: str):
        """
        删除机器人上的地图

        :param map_name: 地图名(不能包含中文等非法字符, 只能使用 0-9, a-z, A-Z, -, _)
        """
        return self.request(4012, 1, {"map_name": map_name})

    def robot_config_push_req(self, interval: int = None, included_fields=None,
                              excluded_fields=None, persistent: bool = None):
        """
        配置推送端口 19301\n
        include_fields 和 exclude_fields 不可同时设置

        :param interval: 消息推送时间间隔（ms）
        :param included_fields: 设置消息中包含的字段
        :param excluded_fields: 设置消息中排除的字段
        :param persistent: 设置该配置是否持久化保存（重启有效）
        """
        d = {}
        if interval is not None:
            d["interval"] = interval
        if included_fields is not None:
            d["included_fields"] = included_fields
        if excluded_fields is not None:
            d["excluded_fields"] = excluded_fields
        if persistent is not None:
            d["persistent"] = persistent
        if d:
            return self.request(4091, 1, d)
        return self.request(4091)

    def robot_config_setparams_req(self, **kwargs):
        """
        临时修改机器人参数\n
        请参考查询机器人参数，来设置参数。机器人重启后，临时修改的参数将会失效。请求数据为 JSON object，其中每一个 key 为不同的插件名，
        value 为 JSON object，代表当前插件中需要修改的参数

        :param kwargs: 参阅 https://books.seer-group.com/public/netprotocol/3.3/zh/dev-integration/netprotocol/tcp-ip/config-api/robot-config-setparams.html
        """
        return self.request(4100, 1, kwargs)

    def robot_config_saveparams_req(self, **kwargs):
        """
        永久修改机器人参数
        请参考查询机器人参数，来设置参数。机器人重启后，永久修改的参数不会失效。请求数据为 JSON object，其中每一个 key 为不同的插件名，
        value 为 JSON object，代表当前插件中需要修改的参数

        :param kwargs: 参阅 https://books.seer-group.com/public/netprotocol/3.3/zh/dev-integration/netprotocol/tcp-ip/config-api/robot-config-saveparams.html
        """
        return self.request(4101, 1, kwargs)

    def robot_config_reloadparams_req(self, params: list = None):
        """
        恢复机器人参数为默认值\n
        请参考查询机器人参数，来设置需要恢复默认值的参数。请求数据为 JSON object array，其中每一个 object 代表一个插件需要恢复为默认值的参数，
        若请求数据为空 JSON object array，则恢复所有插件所有参数为默认值

        :param params: 参阅 https://books.seer-group.com/public/netprotocol/3.3/zh/dev-integration/netprotocol/tcp-ip/config-api/robot-config-reloadparams.html
        """
        if params:
            return self.request(4102, 1, params)
        return self.request(4102)

    def robot_config_ultrasonic_req(self, id: int, valid: bool):
        """
        配置超声\n
        用于配置某个 ID 的超声是否启用
        :param id: 	超声的 ID
        :param valid: 是否启动, false = 禁用, true = 启用
        """
        return self.request(4130, 1, {"id": id, "valid": valid})

    def robot_config_DI_req(self, id: int, valid: bool):
        """
        配置 DI\n
        用于配置某个 id 的 DI 是否启用

        :param id: DI 的 id
        :param valid: 是否启用, false = 禁用, true = 启用
        """
        return self.request(4140, 1, {"id": id, "valid": valid})

    def robot_config_motor_calib_req(self, motor_name: str):
        """
        电机标零

        :param motor_name: 目前仅支持 spin 电机，其他类型的电机无视该指令
        """
        return self.request(4150, 1, {"motor_name": motor_name})

    def robot_config_motor_clear_fault_req(self, motor_name: str):
        """
        电机清错

        :param motor_name: 电机名称（机器人模型中）
        """
        return self.request(4151, 1, {"motor_name": motor_name})

    def robot_config_model_req(self, modelPath: str):
        """
        上传模型文件到机器人

        :param modelPath: 模型文件路径
        """
        with open(modelPath, "rb") as f:
            d = f.read()
        return self.request(4200, 1, d)

    def robot_config_addobstacle_req(self, name: str, x1: float, y1: float, x2: float, y2: float,
                                     x3: float, y3: float, x4: float, y4: float):
        """
        插入动态障碍物(机器人坐标系)\n
        插入机器人坐标系下的矩形动态障碍物,在服务器收到动态障碍物详细坐标时，会在机器人坐标系相应坐标添加name字段数据的障碍物

        :param name: 障碍物名称, 需要唯一
        :param x1: 矩形第一个顶点的 x 坐标(机器人坐标系), 单位 m
        :param y1: 矩形第一个顶点的 y 坐标(机器人坐标系), 单位 m
        :param x2: 矩形第二个顶点的 x 坐标(机器人坐标系), 单位 m
        :param y2: 矩形第二个顶点的 y 坐标(机器人坐标系), 单位 m
        :param x3: 矩形第三个顶点的 x 坐标(机器人坐标系), 单位 m
        :param y3: 矩形第三个顶点的 y 坐标(机器人坐标系), 单位 m
        :param x4: 矩形第四个顶点的 x 坐标(机器人坐标系), 单位 m
        :param y4: 矩形第四个顶点的 y 坐标(机器人坐标系), 单位 m
        """
        d = {"name": name, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "x3": x3, "y3": y3, "x4": x4, "y4": y4}
        return self.request(4350, 1, d)

    def robot_config_addgobstacle_req(self, name: str, x1: float, y1: float, x2: float, y2: float,
                                      x3: float, y3: float, x4: float, y4: float):
        """
        插入动态障碍物(世界坐标系)\n
        插入世界坐标系下的矩形动态障碍物,在服务器收到动态障碍物详细坐标时，会在世界坐标系相应坐标添加name字段数据的障碍物

        :param name: 障碍物名称, 需要唯一
        :param x1: 矩形第一个顶点的 x 坐标(世界坐标系), 单位 m
        :param y1: 矩形第一个顶点的 y 坐标(世界坐标系), 单位 m
        :param x2: 矩形第二个顶点的 x 坐标(世界坐标系), 单位 m
        :param y2: 矩形第二个顶点的 y 坐标(世界坐标系), 单位 m
        :param x3: 矩形第三个顶点的 x 坐标(世界坐标系), 单位 m
        :param y3: 矩形第三个顶点的 y 坐标(世界坐标系), 单位 m
        :param x4: 矩形第四个顶点的 x 坐标(世界坐标系), 单位 m
        :param y4: 矩形第四个顶点的 y 坐标(世界坐标系), 单位 m
        """
        d = {"name": name, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "x3": x3, "y3": y3, "x4": x4, "y4": y4}
        return self.request(4351, 1, d)

    def robot_config_removeobstacle_req(self, name: str = None):
        """
        移除动态障碍物\n

        :param name: 插入过的障碍物名称, 如果缺省, 则移除所有插入过的动态障碍物
        """
        if name:
            return self.request(4352, 1, {"name": name})
        return self.request(4352)

    def robot_config_clear_goodsshape_req(self):
        """
        清除货架描述文件
        """
        return self.request(4356)

    def robot_config_set_shelfshape_req(self, object_path: str):
        """
        设置当前使用的货架描述文件

        :param object_path: 货架描述文件相对路径(不能包含中文等非法字符, 只能使用 0-9, a-z, A-Z, -, _)
        """
        return self.request(4357, 1, {"object_path": object_path})

    def robot_config_send_canframe_req(self, channel: int = None, id: int = None, dlc: int = None, extend: bool = None,
                                       data: str = ""):
        d = {}
        if channel is not None:
            d["channel"] = channel
        if id is not None:
            d["id"] = id
        if dlc is not None:
            d["dlc"] = dlc
        if extend is not None:
            d["extend"] = extend
        if data:
            d["data"] = data
        if d:
            return self.request(4400, 1, d)
        return self.request(4400)

    def robot_config_reset_gnss_req(self, id: str = ""):
        """
        重置 GNSS 硬件配置

        :param id: 	GNSS id
        """
        if id:
            return self.request(4460, 1, {"id": id})
        return self.request(4460)

    def robot_config_set_gnss_baudrate_req(self, id: str = ""):
        """
        配置 GNSS 默认波特率

        :param id: GNSS id
        """
        if id:
            return self.request(4461, 1, {"id": id})
        return self.request(4461)

    def robot_config_set_gnss_rover_req(self, id: str = ""):
        """
        配置 GNSS 为 Rover 模式

        :param id: GNSS id
        """
        if id:
            return self.request(4462, 1, {"id": id})
        return self.request(4462)

    def robot_config_seterror_req(self, msg: str):
        """
        设置第三方 Error\n
        设置后会产生 52900 的 Error 报警码，机器人停止运动，Roboshop 可以看到如下报警： "an error" 为 msg 中传入的内容。

        :param msg: Error 的描述，仅限英文
        """
        return self.request(4800, 1, {"msg": msg})

    def robot_config_clearerror_req(self):
        """
        清除第三方 Error\n
        用于清除 52900 的 Error 报警码。
        """
        return self.request(4801)

    def robot_config_setwarning_req(self, msg: str):
        """
        设置第三方 Warning\n
        设置后会产生 54900 的 Warning 报警码，Roboshop 可以看到如下报警： "a warning" 为 msg 中传入的内容。

        :param msg: Warning 的描述，仅限英文
        """
        return self.request(4802, 1, {"msg": msg})

    def robot_config_clearwarning_req(self):
        """
        清除第三方 Warning\n
        用于清除 54900 的 Warning 报警码。
        """
        return self.request(4803)

    def robot_config_clear_odo_req(self):
        '''
        运位信息复位
        设置后将累计里程，今日累计里程，累计运行时间，本次运行时间清零
        '''
        return self.request(4450)

    # 以下是其他 API
    # 其他 API 包含各种杂项，如播放音频、DO 控制、货叉控制、辊筒皮带控制等。

    def robot_other_play_audio_req(self, name: str, loop: bool = False):
        """
        播放音频, 播放指定的音频文件

        :param name: 需要播放的音频文件名(不含文件扩展名)
        :param loop: 是否循环播放(true = 循环, false = 不循环,如果缺省则默认不循环)
        """
        return self.request(6000, 1, {"name": name, "loop": loop})

    def robot_other_update_transparent_data_req(self, **kwargs):
        """
        更新透传数据
        """
        return self.request(6900, 1, kwargs)

    def robot_other_setdo_req(self, id: int, status: bool):
        """
        设置 DO\n
        该 API 用于设置机器人控制器上的 DO (Digital Output) 状态

        :param id: 	DO 的 id
        :param status: true 为高电平, false 为低电平
        """
        return self.request(6001, 1, {"id": id, "status": status})

    def robot_other_setdos_req(self, dos: list):
        """
        批量设置 DO\n
        该 API 用于批量设置机器人控制器上的 DO (Digital Output) 状态

        :param dos: 数组每个成员为包含id和status的字典，示例：[{"id":0,"status":true},{"id":1,"status":true}]
        """
        return self.request(6002, 1, dos)

    def robot_other_setrelay_req(self, status: bool):
        """
        设置继电器\n
        该 API 用于设置机器人控制器上的继电器状态

        :param status: true 为继电器吸合, false 为继电器断开
        """
        return self.request(6003, 1, {"status": status})

    def robot_other_softemc_req(self, status: bool):
        """
        软急停\n
        该 API 用于通过软件的方式控制机器人控制器是否输出急停信号

        :param status: true 为输出急停, false 为不输出急停
        """
        return self.request(6004, 1, {"status": status})

    def robot_other_setchargingrelay_req(self, status: bool):
        """
        设置充电继电器\n
        该 API 用于设置机器人充电继电器状态

        :param status: true 为充电继电器吸合, false 为充电继电器断开
        """
        return self.request(6005, 1, {"status": status})

    def robot_other_pause_audio_req(self):
        """
        暂停播放音频
        """
        return self.request(6010)

    def robot_other_resume_audio_req(self):
        """
        继续播放音频\n
        将从暂停处继续播放
        """
        return self.request(6011)

    def robot_other_stop_audio_req(self):
        """
        停止播放音频\n
        直接结束音频的播放
        """
        return self.request(6012)

    def robot_other_setvdi_req(self, id: int, status: bool):
        """
        设置虚拟 DI\n
        该 API 用于设置机器人控制器上的虚拟 DI (Virtual Digital Iutput) 状态

        :param id: 虚拟 DI 的 id (DI 列表中第一个虚拟 DI 的索引(index) 为 0, id 范围 [0, 7])
        :param status: true 为高电平, false 为低电平
        """
        return self.request(6020, 1, {"id": id, "status": status})

    def robot_other_audio_list_req(self):
        """
        获取音频文件列表
        """
        return self.request(6033)

    def robot_other_set_fork_height_req(self, height: float):
        """
        设置货叉高度\n
        该 API 用于设置叉车的货叉高度, 该指令会立即返回, 需通过 1028 或 1100 指令中的 fork_height_in_place 来查询货叉是否到位\n
        机器人运动过程中不接受辊筒运动指令

        :param height: 	货叉高度, 单位 m 针对地牛：1=上升；0=下降
        """
        return self.request(6040, 1, {"height": height})

    def robot_other_stop_fork_req(self):
        """
        停止货叉\n
        该 API 用于停止叉车的货叉运动
        """
        return self.request(6041)

    def robot_other_set_fork_forward_req(self, forward: float):
        """
        设置货叉前移后退\n
        该 API 用于设置叉车的货叉前移后退, 该指令会立即返回, 需通过 1028 或 1100 指令中的 forward_in_place 来查询货叉是否到位

        :param forward: 没有拉线编码器：2 = 前移，1 = 后移，0 = 停止。
                        有拉线编码器：正数表示前移距离，负数表示后退距离, 单位 m
        """
        return self.request(6042, 1, {"forward": forward})

    def robot_other_write_peripheral_data_req(self, id: int, data: int):
        """
        写入外设用户自定义数据

        :param id: id 号, 0~15
        :param data: 寄存器数据
        """
        return self.request(6049, 1, {"id": id, "data": data})

    def robot_other_roller_front_roll_req(self):
        """
        辊筒(皮带)向前滚动\n
        滚动时两侧挡板均放下,该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询滚动是否完成。
        滚动不会因超时而失败，辊筒会一直转动，直到接收新的指令。机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6051)

    def robot_other_roller_back_roll_req(self):
        """
        辊筒(皮带)向后滚动\n
        滚动时两侧挡板均放下,该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询滚动是否完成。
        滚动不会因超时而失败，辊筒会一直转动，直到接收新的指令。机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6052)

    def robot_other_roller_left_roll_req(self):
        """
        辊筒(皮带)向左滚动\n
        滚动时两侧挡板均放下,该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询滚动是否完成。
        滚动不会因超时而失败，辊筒会一直转动，直到接收新的指令。机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6053)

    def robot_other_roller_right_roll_req(self):
        """
        辊筒(皮带)向右滚动\n
        滚动时两侧挡板均放下,该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询滚动是否完成。
        滚动不会因超时而失败，辊筒会一直转动，直到接收新的指令。机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6054)

    def robot_other_roller_front_load_req(self):
        """
        辊筒(皮带)前上料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询上料是否完成。前上料可能会因超时而失败。
        机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6055)

    def robot_other_roller_front_unload_req(self):
        """
        辊筒(皮带)前下料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询下料是否完成。前下料可能会因超时而失败。
        机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6056)

    def robot_other_roller_front_pre_load_req(self):
        """
        辊筒(皮带)前预上料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询预上料是否完成。预上料不会因超时而失败，
        辊筒会一直转动，直到接收新的指令。机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6057)

    def robot_other_roller_back_load_req(self):
        """
        辊筒(皮带)后上料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询上料是否完成。后上料可能会因超时而失败。
        机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6058)

    def robot_other_roller_back_unload_req(self):
        """
        辊筒(皮带)后下料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询下料是否完成。后下料可能会因超时而失败。
        机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6059)

    def robot_other_roller_back_pre_load_req(self):
        """
        辊筒(皮带)后预上料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询预上料是否完成。预上料不会因超时而失败，辊筒会一直转动，
        直到接收新的指令。机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6060)

    def robot_other_roller_left_load_req(self):
        """
        辊筒(皮带)左上料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询上料是否完成。左上料可能会因超时而失败。
        机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6061)

    def robot_other_roller_left_unload_req(self):
        """
        辊筒(皮带)左下料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询下料是否完成。左下料可能会因超时而失败。
        机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6062)

    def robot_other_roller_right_load_req(self):
        """
        辊筒(皮带)右上料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询上料是否完成。右上料可能会因超时而失败。
        机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6063)

    def robot_other_roller_right_unload_req(self):
        """
        辊筒(皮带)右下料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询上料是否完成。右上料可能会因超时而失败。
        机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6064)

    def robot_other_roller_left_pre_load_req(self):
        """
        辊筒(皮带)左预上料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询预上料是否完成。预上料不会因超时而失败，
        辊筒会一直转动，直到接收新的指令。机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6065)

    def robot_other_roller_right_pre_load_req(self):
        """
        辊筒(皮带)右预上料\n
        该指令会立即返回, 需通过 1029 或 1100 指令中的 roller_state 来查询预上料是否完成。预上料不会因超时而失败，
        辊筒会一直转动，直到接收新的指令。机器人运动过程中不接受辊筒运动指令
        """
        return self.request(6066)

    def robot_other_roller_stop_req(self):
        """
        辊筒(皮带)停止
        """
        return self.request(6067)

    def robot_other_roller_left_right_inverse_req(self, inverse: bool):
        """
        辊筒(皮带)左右反向\n
        使用该指令设置反向后，辊筒的左右逻辑会相反，即左上料变为右上料，右上料变为左上料。
        :param inverse: 是否反向，true = 反向, false = 不反向(即恢复正常)
        """
        return self.request(6068, 1, {"inverse": inverse})

    def robot_other_roller_front_back_inverse_req(self, inverse: bool):
        """
        辊筒(皮带)前后反向\n
        使用该指令设置反向后，辊筒的前后逻辑会相反，即前上料变为后上料，后上料变为前上料。。
        :param inverse: 是否反向，true = 反向, false = 不反向(即恢复正常)
        """
        return self.request(6069, 1, {"inverse": inverse})

    def robot_other_jack_load_req(self):
        """
        顶升机构上升\n
        该指令会立即返回, 需通过 1027 或 1100 指令中的 jack_state 来查询顶升状态
        """
        return self.request(6070)

    def robot_other_jack_unload_req(self):
        """
        顶升机构下降\n
        该指令会立即返回, 需通过 1027 或 1100 指令中的 jack_state 来查询顶升状态
        """
        return self.request(6071)

    def robot_other_jack_stop_req(self):
        """
        顶升机构停止\n
        该指令会立即返回, 需通过 1027 或 1100 指令中的 jack_state 来查询顶升状态
        """
        return self.request(6072)

    def robot_other_jack_set_height_req(self, height: float):
        """
        顶升调整至固定高度\n
        该指令会立即返回, 需通过 1027 或 1100 指令中的 jack_state 来查询顶升状态

        :param height: 顶升的高度, 单位 m
        """
        return self.request(6073, 1, {"height": height})

    def robot_other_reset_cargo_req(self):
        """
        清除载荷状态\n
        该 API 用于清除载荷状态
        """
        return self.request(6080)

    def robot_other_hook_load_req(self):
        """
        牵引上料\n
        后置牵引机构夹取托车
        """
        return self.request(6082)

    def robot_other_hook_unload_req(self):
        """
        牵引下料\n
        后置牵引机构松开托车
        """
        return self.request(6083)

    def robot_other_slam_req(self, real_time: bool = None, screen_width: float = None, screen_height: float = None):
        """
        开始扫描地图\n
        如果要接受实时的扫图数据, 请监听 UDP 19301 端口, 数据格式为二进制的 rbk.protocol.Message_MapLog\n
        如果要接受实时的扫图图像画面, 请求 HTTP 9301 端口，url: http://ip:9301/slam 方法为Get，content-type 为：image/png

        :param real_time: 是否开启实时扫图数据传输,默认为 false
        :param screen_width: 扫描屏幕宽度, 单位 像素
        :param screen_height: 扫描屏幕高度, 单位 像素
        """
        d = {}
        if real_time is not None:
            d["real_time"] = real_time
        if screen_width is not None:
            d["screen_width"] = screen_width
        if screen_height is not None:
            d["screen_height"] = screen_height
        if d:
            return self.request(6100, 1, d)
        return self.request(6100)

    def robot_other_endslam_req(self):
        """
        停止扫描地图
        """
        return self.request(6101)

    def robot_other_set_motors_req(self):
        """
        电机调试\n
        弃用
        """
        pass

    def robot_other_set_motor_enable_req(self, motor_name: str, enable: bool):
        """
        电机使能与去使能\n

        :param motor_name: 电机名
        :param enable: true = 使能, false = 去使能
        """
        return self.request(6201, 1, {"motor_name": motor_name, "enable": enable})

    def robot_other_clear_goods_req(self, goods_id: str):
        """
        解绑指定货物\n
        此 API 仅对料箱车有效，PS：料箱车指在机器人模型文件中配置了 container 的车,
        有关料箱车 container 详细信息查询可以参考，机器人导航状态或者批量数据1

        :param goods_id: 货物ID
        """
        return self.request(6801, 1, {"goods_id": goods_id})

    def robot_other_clear_container_req(self, container_name: str):
        """
        从指定料箱解绑货物\n
        此 API 仅对料箱车有效，PS：料箱车指在机器人模型文件中配置了 container 的车,
        有关料箱车 container 详细信息查询可以参考，机器人导航状态或者批量数据1

        :param container_name: 料箱名（在模型文件中配置container）
        """
        return self.request(6802, 1, {"container_name": container_name})

    def robot_other_clear_all_containers_goods_req(self):
        """
        从所有料箱解绑货物\n
        此 API 仅对料箱车有效，PS：料箱车指在机器人模型文件中配置了 container 的车,
        有关料箱车 container 详细信息查询可以参考，机器人导航状态或者批量数据1
        """
        return self.request(6803)

    def robot_other_set_container_goods_req(self, goods_id: str, container_name: str, desc: str):
        """
        绑定货物到料箱\n
        此 API 仅对料箱车有效，PS：料箱车指在机器人模型文件中配置了 container 的车,
        有关料箱车 container 详细信息查询可以参考，机器人导航状态或者批量数据1

        :param goods_id: 货物ID
        :param container_name: 料箱名（在模型文件中配置container）
        :param desc: 货物描述
        """
        return self.request(6804, 1, {"goods_id": goods_id, "container_name": container_name, "desc": desc})

    # 以下是机器人推送API
    def robot_push_config_req(self, interval: int = None, included_fields=None,
                              excluded_fields=None) -> dict:
        """
        配置推送端口 19301\n
        include_fields 和 exclude_fields 不可同时设置

        :param interval: 消息推送时间间隔（ms）
        :param included_fields: 设置消息中包含的字段
        :param excluded_fields: 设置消息中排除的字段
        """

        d = {}
        if interval is not None:
            d["interval"] = interval
        if included_fields is not None:
            d["included_fields"] = included_fields
        if excluded_fields is not None:
            d["excluded_fields"] = excluded_fields
        if included_fields and excluded_fields:
            raise ValueError("included_fields and excluded_fields can not be set at the same time")
        if not d:
            raise ValueError("interval, included_fields or excluded_fields must be set")

        body = bytearray(json.dumps(d), "ascii")
        msgLen = len(body)
        rawMsg = struct.pack(PACK_FMT_STR, 0x5A, 0x01, 1, msgLen, 9300, b'\x00\x00\x00\x00\x00\x00')
        self.so_19301.send(rawMsg + body)
        return json.loads(self.pushData.get())

    def _robot_push(self):
        """
        机器人推送API
        """

        while self.pushThreadFlag:
            # 接收报文头
            headData = self.so_19301.recv(16)
            # 解析报文头
            header = struct.unpack(PACK_FMT_STR, headData)
            # 获取报文体长度
            bodyLen = header[3]
            readSize = 1024
            recvData = b''
            while (bodyLen > 0):
                recv = self.so_19301.recv(readSize)
                recvData += recv
                bodyLen -= len(recv)
                if bodyLen < readSize:
                    readSize = bodyLen
            if self.pushData.full():
                self.pushData.get()
            self.pushData.put(recvData)


# if __name__ == "__main__":
#     r = rbklib(ip="192.168.133.135")
#     print(r.robot_status_sound_req())
#     # r.robot_config_uploadmap_req(mapPath = "F:/SDK/rbk/AutoTest/test_rbk/test_avoid/aps-d2-saw.smap")
#     # r.robot_control_loadmap_req(map_name = "aps-d2-saw")
#     # r.lock()
#     # data = {"RBKSim":{"RBKSimMinVx":0.5}}
#     # r.modifyParam(data = data)
#     # pos = {"x":-0.525, "y":-0.06, "angle":0}
#     # r.moveRobot(pos=pos)
#     # time.sleep(1.0)
#     # ts = r.getTaskStatus()
#     # while ts is 2:
#     #     ts = r.getTaskStatus()
#     #     time.sleep(1)
#     # if ts["task_status"] == 4:
#     #     print("success! stauts = ", ts["task_status"])
#     # else:
#     #     print("failed! stauts = ", ts["task_status"])
