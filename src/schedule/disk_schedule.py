# -*- coding: utf-8 -*-  
"""
@Date     : 2025-03-13
@Author   : xwq
@Desc     : <None>

"""
import datetime
import logging
import os
import shutil

from src import get_config


def _clear(folder: str, cache_folder: str, cache_limit: int, remove_limit: int):
    now = datetime.datetime.now()

    for filename in os.listdir(cache_folder):
        filepath = os.path.join(cache_folder, filename)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        if (now - mtime).days >= remove_limit:
            try:
                os.remove(filepath)
            except Exception as e:
                logging.warning(f'删除文件失败: {filepath}, {e.__traceback__}')

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        if (now - mtime).days >= cache_limit:
            try:
                shutil.move(filepath, os.path.join(cache_folder, filename))
            except Exception as e:
                logging.warning(f'迁移文件失败: {filepath}, {e.__traceback__}')


def _do_clear(folder: str, cache_folder: str, cache_limit: int = 3, remove_limit: int = 30):
    try:
        _clear(folder, cache_folder, cache_limit, remove_limit)
    except Exception as e:
        logging.warning(f'清理文件失败: {e.__traceback__}')


def clear_files():
    _do_clear(
        get_config('common', 'download_path'),
        get_config('common', 'cache_download_path'),
    )
    _do_clear(
        get_config('common', 'log_path'),
        get_config('common', 'cache_log_path'),
    )
