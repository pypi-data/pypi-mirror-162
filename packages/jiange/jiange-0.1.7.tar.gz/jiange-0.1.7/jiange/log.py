import os
import logging.handlers
from jiange.file import dump_json


class LogAgent():

    def __init__(self):
        self.logger = self.init_log()

    def info(self, body):
        """支持对 str / dict 类型的数据记录日志"""
        if isinstance(body, dict):
            body = dump_json(body, indent=False)
        self.logger.info(body)

    @staticmethod
    def init_log():
        """
        - 日志采用 RotatingFileHandler 方式存储，单个文件最大 5M
        - 存储路径 /tmp/logs/，并以 log.txt, log.txt.1, ... 命名
        """
        path_tgt = '/tmp/logs'
        if not os.path.exists(path_tgt):
            os.mkdir(path_tgt)
        log_file = os.path.join(path_tgt, 'log.txt')
        log_level = logging.INFO
        logger = logging.getLogger("loggingmodule.NomalLogger")
        handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=10, encoding='utf8')
        formatter = logging.Formatter("[%(levelname)s][%(filename)s][%(asctime)s]%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        return logger
