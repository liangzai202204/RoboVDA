import logging
import os
from logging.handlers import TimedRotatingFileHandler
from colorlog import ColoredFormatter


class MyLogger:
    def __init__(self, name="SEER-robokit-VDA5050", interval=15 * 60):
        log_dir = os.getcwd() + "/scripts-logs/"
        filename = "vda5050_debug.log"
        os.makedirs(log_dir, exist_ok=True)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        fh = TimedRotatingFileHandler(
            filename=log_dir + filename,
            when='M',
            interval=interval,
            backupCount=7,
            encoding='utf-8'
        )
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 设置输出格式
        formatter = ColoredFormatter(
            "[%(asctime)s] %(log_color)s[%(name)s] %(levelname)s%(reset)s %(message)s",
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


