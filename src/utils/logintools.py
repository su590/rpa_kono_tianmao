# -*- coding: utf-8 -*-  
"""
@Date     : 2025-02-20
@Author   : xwq
@Desc     : <None>

"""
import dataclasses
import json
import logging
import os
import pickle
import time
import traceback
import uuid
from abc import ABC, abstractmethod

import requests
from DrissionPage.errors import BaseError
from DrissionPage.items import ChromiumTab

from src.config import COMMON_DOWNLOAD_PATH
from src.rds.autopage import AutoTab
from src.rds.flag import Flag
from src.rds.semaphore import Semaphore
from src.utils.cryptotools import cryptotools
from src.utils.pagetools import get_page


@dataclasses.dataclass
class Login(ABC):

    def __init__(self, port: int, username: str):
        self._port = port
        self._username = username
        self._at = AutoTab(self._port)

    @abstractmethod
    def _login(self, tab: ChromiumTab) -> None:
        ...

    def _screenshot(self) -> list[str]:
        """
        截图存证
        """
        prefix = str(uuid.uuid4())

        page = get_page(self._port)
        img_paths = []
        for i, tab in enumerate(page.get_tabs()):
            if i != 0:
                time.sleep(1)
            img_path = os.path.join(COMMON_DOWNLOAD_PATH, f'{prefix}_{i}.png')
            try:
                tab.ele('x://html').get_screenshot(img_path)
            except (BaseError, TimeoutError) as e:
                txt_path = os.path.join(COMMON_DOWNLOAD_PATH, f'{prefix}_{i}_截图失败.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f'{e}\n\n{traceback.format_exc()}')
            else:
                img_paths.append(img_path)
                logging.info(f'登录异常({self.__class__.__name__}), 尝试截图留证 --> {img_path}')

        json_path = os.path.join(COMMON_DOWNLOAD_PATH, f'{prefix}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps({
                'class': self.__class__,
                'dict': self.__dict__
            }, ensure_ascii=False, indent=4, default=str))

        return img_paths

    def _error(self):
        self._screenshot()

    def _do_login(self) -> ChromiumTab:
        tab = self._at.__enter__()
        try:
            self._login(tab)
        except Exception as e:
            logging.error(f'登录时出现未知异常: {e} >> {traceback.format_exc()}')
            try:
                self._error()
            finally:
                self.__exit__(type(e), e, e.__traceback__)
                raise e
        else:
            return tab

    def __enter__(self) -> ChromiumTab:
        Semaphore(f'login-{self._port}').acquire()
        return self._do_login()

    def __exit__(self, exc_type, exc_val, exc_tb):
        Semaphore(f'login-{self._port}').release()
        return self._at.__exit__(exc_type, exc_val, exc_tb)

    def mktab(self) -> ChromiumTab:
        return self._at.mktab()


_SESSIONS: dict[str, requests.Session] = {}


class Session(ABC):

    def __init__(self, port: int, username: str):
        self._port = port
        self._username = username

    def _session_key(self) -> str:
        return cryptotools.md5(pickle.dumps((self.__class__, self.__dict__)))

    @abstractmethod
    def _session(self) -> requests.Session:
        pass

    def __enter__(self) -> requests.Session:
        session_key = self._session_key()
        flag = Flag(session_key)
        if not flag.exist():
            _SESSIONS.pop(session_key, None)
            session = None
        else:
            session = _SESSIONS.get(session_key)
        if session is not None:
            return session

        with Semaphore(f'session:{self._port}'):
            if not flag.exist():
                _SESSIONS.pop(session_key, None)
                session = None
            else:
                session = _SESSIONS.get(session_key)
            if session is not None:
                return session
            session = self._session()
            _SESSIONS[session_key] = session
            flag.save(timeout=60 * 30)
            return session

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
