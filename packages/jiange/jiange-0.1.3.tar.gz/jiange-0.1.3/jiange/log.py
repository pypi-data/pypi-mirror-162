import logging.handlers
import os


def local_log():
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


logger = local_log()
