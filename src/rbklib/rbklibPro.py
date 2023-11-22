import asyncio
import json
import struct
import threading
import socket
import time
from src.log.log import MyLogger
from src.serve.topicQueue import TopicQueue


class Rbk:

    def __init__(self, ip: str):
        self.ip = ip
        self.log = MyLogger()
        self.so_19301 = So19301(self.ip)
        self.so_19204 = So19204(self.ip)
        self.so_19205 = So19205(self.ip)
        self.so_19206 = So19206(self.ip)
        self.so_19207 = So19207(self.ip)
        self.so_19210 = So19210(self.ip)
        self.online_status = dict()

    def connect(self):
        self.so_19301.connect_push()
        self.so_19204.connect()
        self.so_19205.connect()
        self.so_19206.connect()
        self.so_19207.connect()
        self.so_19210.connect()

    @property
    def online(self):
        self.online_status = {
            "19204": self.so_19204.connected,
            "19205": self.so_19205.connected,
            "19206": self.so_19206.connected,
            "19207": self.so_19207.connected,
            "19301": self.so_19301.connected
        }
        if self.so_19204.connected and self.so_19205.connected and self.so_19206.connected \
                and self.so_19207.connected and self.so_19301.connected:
            return True
        else:

            return False

    def __del__(self):
        if self.so_19204 is not None:
            self.so_19204.so.close()
        if self.so_19205 is not None:
            self.so_19205.so.close()
        if self.so_19206 is not None:
            self.so_19206.so.close()
        if self.so_19207 is not None:
            self.so_19207.so.close()
        if self.so_19210 is not None:
            self.so_19210.so.close()
        if self.so_19301 is not None:
            self.so_19301.so.close()

    def request(self, msgType, msg=None, reqId=1):
        print("request:", msgType)
        if 1000 <= msgType < 2000:
            return self.so_19204.request(msgType, reqId, msg)
        elif msgType < 3000:
            return self.so_19205.request(msgType, reqId, msg)
        elif msgType < 4000:
            return self.so_19206.request(msgType, reqId, msg)
        elif msgType < 5000:
            return self.so_19207.request(msgType, reqId, msg)
        elif 6000 <= msgType < 7000:
            return self.so_19210.request(msgType, reqId, msg)
        elif 9000 <= msgType < 9999:
            return self.so_19301.request(msgType, reqId, msg)
        else:
            # 如果报文类型不在范围内，则抛出异常
            raise ValueError("没有与报文类型对应的socket,或者需要指定一个socket")

    def call_service(self, *request):
        if request.__len__() == 1:
            return self.request(request[0])
        else:
            return self.request(request[0], request[1])


class BaseSo:
    def __init__(self, ip: str, port: int, socket_timeout=60, max_reconnect_attempts=10):
        self.PACK_FMT_STR = '!BBHLH6s'
        self.log = MyLogger()
        self.ip = ip
        self.port = port
        self.so = None
        self.connected = False
        self.socket_timeout = socket_timeout
        self.reconnect_attempts = 0  # 重连尝试次数
        self.max_reconnect_attempts = max_reconnect_attempts  # 最大重连尝试次数
        self.initial_reconnect_delay = 1  # 初始重连延迟（秒）
        self.max_reconnect_delay = 60  # 最大重连延迟（秒）

    def connect(self):
        while not self.connected:
            try:
                self.so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.so.setblocking(False)
                self.so.settimeout(self.socket_timeout)

                self.so.connect((self.ip, self.port))
                self.connected = True
                self.log.info(f"[rbk]connect rbk({self.ip}:{self.port}) ok!")
            except Exception as e:
                self.log.warning(f"连接失败：{e}")
                self.connected = False
                self.reconnect_attempts += 1

                if self.reconnect_attempts > self.max_reconnect_attempts:
                    self.log.warning(f"达到最大重连尝试次数，繼續重新鏈接")
                    self.reconnect_attempts = 0
                    self.initial_reconnect_delay = 1
                reconnect_delay = self.get_reconnect_delay()
                self.log.warning(f"等待 {reconnect_delay} 秒后进行重连")
                time.sleep(reconnect_delay)

    def _request(self, so: socket.socket, msgType, reqId=1, msg=None):
        """
        发送请求
        :param msgType: 报文类型
        :param reqId: 序号
        :param msg: 消息体/数据区
        :param so:  使用指定的socket
        :return: 响应，包含报文头和报文体的元组，报文头[2：序号 3：报文体长度 4：报文类型]
        """
        ################################################################################################################
        # 打印socket信息
        # print("*" * 20, "socket信息", "*" * 20)
        # print(f"{'socket:':>10}\server{so.getpeername()},local{so.getsockname()}")
        # print()
        ################################################################################################################
        # 封装报文

        body = None
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
        rawMsg = struct.pack(self.PACK_FMT_STR, 0x5A, 0x01, reqId, msgLen, msgType, b'\x00\x00\x00\x00\x00\x00')
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
        header = struct.unpack(self.PACK_FMT_STR, headData)
        # 获取报文体长度
        bodyLen = header[3]
        readSize = 1024
        recvData = b''
        while bodyLen > 0:

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

    def request(self, msgType, reqId=1, msg=None):
        if not self.connected:
            self.log.warning("未连接到服务器")
            return None
        try:
            h, body = self._request(self.so, msgType, reqId, msg)
            # print(body)
            return body
        except socket.timeout:
            self.connected = False
            self.log.warning("连接超时异常，重新连接")
            self.reconnect()
        except ConnectionResetError:
            self.connected = False
            self.log.warning("连接重置异常，重新连接")
            self.reconnect()
        except Exception as e:
            self.connected = False
            self.reconnect()
            self.log.warning(f"其他异常：{e}")

    def reconnect(self):
        self.so.close()  # 关闭原有的套接字
        self.so = None
        reconnect_delay = self.get_reconnect_delay()
        self.log.warning(f"等待 {reconnect_delay} 秒后进行重连")
        time.sleep(reconnect_delay)
        self.connect()

    def get_reconnect_delay(self):
        # 使用指数退避算法计算重连延迟
        reconnect_delay = self.initial_reconnect_delay * 2 ** (self.reconnect_attempts - 1)
        return min(reconnect_delay, self.max_reconnect_delay)


class So19204(BaseSo):
    def __init__(self, ip: str = "127.0.0.1", socket_timeout=60, max_reconnect_attempts=5):
        super().__init__(ip, 19204, socket_timeout, max_reconnect_attempts)

    @property
    def get_connected(self):
        return self.so.connected


class So19205(BaseSo):
    def __init__(self, ip: str = "127.0.0.1", socket_timeout=60, max_reconnect_attempts=5):
        super().__init__(ip, 19205, socket_timeout, max_reconnect_attempts)

    @property
    def get_connected(self):
        return self.so.connected


class So19206(BaseSo):
    def __init__(self, ip: str = "127.0.0.1", socket_timeout=60, max_reconnect_attempts=5):
        super().__init__(ip, 19206, socket_timeout, max_reconnect_attempts)

    @property
    def get_connected(self):
        return self.so.connected


class So19207(BaseSo):
    def __init__(self, ip: str = "127.0.0.1", socket_timeout=60, max_reconnect_attempts=5):
        super().__init__(ip, 19207, socket_timeout, max_reconnect_attempts)

    @property
    def get_connected(self):
        return self.so.connected


class So19210(BaseSo):
    def __init__(self, ip: str = "127.0.0.1", socket_timeout=60, max_reconnect_attempts=5):
        super().__init__(ip, 19210, socket_timeout, max_reconnect_attempts)

    @property
    def get_connected(self):
        return self.so.connected


class So19301(BaseSo):
    def __init__(self, ip: str = "127.0.0.1", socket_timeout=60, max_reconnect_attempts=5, pushDataSize=50):
        super().__init__(ip, 19301, socket_timeout, max_reconnect_attempts)
        print(ip,self.port)
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=_run_loop, args=(self.loop,), daemon=True)

    def connect_push(self):
        self.connect()
        self.loop.call_soon_threadsafe(self.loop.create_task, self.robot_push())
        self.thread.start()

    @property
    def get_connected(self):
        return self.so.connected

    async def robot_push(self):
        """
        机器人推送API
        """

        while True:
            # 接收报文头
            try:
                await self.recv()

            except Exception as e:
                self.log.warning(f"获取机器人数据失败：{e}")
                self.connected = False
                self.reconnect()
                return None

    async def recv(self):
        headData = self.so.recv(16)
        # 解析报文头
        header = struct.unpack(self.PACK_FMT_STR, headData)
        # 获取报文体长度
        bodyLen = header[3]
        readSize = 1024
        recvData = b''
        while bodyLen > 0:
            recv = self.so.recv(readSize)
            recvData += recv
            bodyLen -= len(recv)
            if bodyLen < readSize:
                readSize = bodyLen
        # 检查是否接收到完整的报文体
        if len(recvData) == header[3]:
            # self.log.warning(f"19301 push raw data:{recvData}")
            if TopicQueue.pushData.full():
                await TopicQueue.pushData.get()
            await TopicQueue.pushData.put(recvData)
        else:
            self.log.warning(f"接收到不完整的报文体，继续接收...")

    def get(self):
        try:
            # 接收报文头
            headData = self.so.recv(16)
            # 解析报文头
            header = struct.unpack(self.PACK_FMT_STR, headData)
            # 获取报文体长度
            bodyLen = header[3]
            recvData = b''
            while len(recvData) < bodyLen:
                recv = self.so.recv(bodyLen - len(recvData))
                if not recv:
                    break
                recvData += recv
            return recvData
        except Exception as e:
            print(f"获取机器人数据失败：{e}")
            self.connected = False
            self.reconnect()
            return None


def _run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
