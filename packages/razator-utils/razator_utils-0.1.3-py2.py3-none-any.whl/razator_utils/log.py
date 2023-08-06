import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE_MAX_BYTES = 1024 * 1024 * 10  # 10 megabytes


def define_script_logger(dev, script_name, log_path=None, level=logging.WARNING):
    if dev:
        return get_stout_logger(script_name, level=level)
    else:
        if log_path is None:
            log_path = Path.home() / '.logs' / f'{script_name}.log'
        return get_file_logger(script_name, log_path, level=level, backup_count=1)


def __get_log_formatter__():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    formatter.converter = time.gmtime
    return formatter


def __get_logger__(name, level=logging.WARNING):
    logger = logging.getLogger(name)
    if isinstance(level, str):
        level = level.upper()
    logger.setLevel(level)
    return logger


def __add_handler__(name, handler, level, logger=None):
    if not logger:
        logger = __get_logger__(name, level)
    logger.addHandler(handler)
    return logger


def get_stout_logger(name, level=logging.WARNING):
    handler = logging.StreamHandler()
    handler.setFormatter(__get_log_formatter__())
    return __add_handler__(name, handler, level)


def get_file_logger(name, log_file_path, level=logging.WARNING, max_bytes=LOG_FILE_MAX_BYTES, backup_count=1):
    handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(__get_log_formatter__())
    return __add_handler__(name, handler, level)
