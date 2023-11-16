import re
import logging
import os
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter
from datetime import datetime


class MyLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MyLogger, cls).__new__(cls, *args, **kwargs)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, name="SEER-robokit-VDA5050", max_bytes=1024 * 1024):
        if self.__initialized:
            return
        self.__initialized = True

        log_dir = os.getcwd() + "/scripts-logs/"
        os.makedirs(log_dir, exist_ok=True)

        # 获取已有的日志文件名列表
        existing_logs = [filename for filename in os.listdir(log_dir) if re.match(r".*\.log(\.\d+)?", filename)]
        existing_logs.sort(reverse=True)

        # 删除超出限定数量的部分日志文件
        if len(existing_logs) > 10:
            logs_to_delete = existing_logs[10:]
            for log in logs_to_delete:
                os.remove(os.path.join(log_dir, log))

        # 计算当前时间段
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")

        # 获取当前日志文件名的尾部数字
        log_number = -1
        if existing_logs:
            last_log = existing_logs[0]
            log_number = int(re.search(r"\.log\.(\d+)$", last_log).group(1)) if re.search(r"\.log\.(\d+)$", last_log) else -1

        # 创建新的日志文件名
        log_number += 1
        if log_number >= 0:
            filename = f"vda5050_debug_{timestamp}_{log_number:05d}.log"
        else:
            filename = f"vda5050_debug_{timestamp}.log"

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        fh = RotatingFileHandler(
            filename=os.path.join(log_dir, filename),
            maxBytes=max_bytes,
            backupCount=10,
            encoding='utf-8'
        )
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 设置输出格式
        formatter = ColoredFormatter(
            "[%(asctime)s.%(msecs)03d] %(log_color)s[%(name)s] %(levelname)s%(reset)s %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            reset=True,
            style='%'
        )

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 将handler添加到logger中
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
