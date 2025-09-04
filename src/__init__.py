import logging
import os

from src.config import get_config
from src.utils.logtools import logtools


def _init_folder():
    folders = [
        get_config('drissionpage', 'user_data_path'),
        get_config('drissionpage', 'download_path'),
        get_config('common', 'download_path'),
        get_config('common', 'log_path'),
        get_config('common', 'cache_download_path'),
        get_config('common', 'cache_log_path'),
    ]
    for folder in folders:
        if os.path.exists(folder):
            continue
        os.makedirs(folder, exist_ok=True)


def _init_log():
    logger = logging.getLogger()
    # 日志基础级别
    logger.setLevel(logging.DEBUG)
    # 日志格式
    fmt = '%(asctime)s %(levelname)s %(name)s (%(thread)d): %(message)s'
    # 控制台多色
    logtools.colorlog(logging.getLogger(), level=logging.INFO, fmt=fmt)
    # 日志文件
    folder = get_config('common', 'log_path')
    logtools.dailylog(logger, folder=folder, level=logging.DEBUG, fmt=fmt, datefmt='%Y%m%d DEBUG')
    logtools.dailylog(logger, folder=folder, level=logging.INFO, fmt=fmt, datefmt='%Y%m%d INFO')
    logtools.dailylog(logger, folder=folder, level=logging.WARNING, fmt=fmt, datefmt='%Y%m%d WARNING')
    logtools.dailylog(logger, folder=folder, level=logging.ERROR, fmt=fmt, datefmt='%Y%m%d ERROR')


_init_folder()
_init_log()
