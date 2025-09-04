import logging
import pickle
import threading
import time

from DrissionPage import ChromiumPage
from DrissionPage.items import ChromiumTab

from src.rds import REDIS, PREFIX
from src.rds.semaphore import Semaphore
from src.utils.cryptotools import cryptotools
from src.utils.pagetools import get_page

_STATUS = f'{PREFIX}:autopage:status'
_CACHE = f'{PREFIX}:autopage:cache'


class _Key:
    @classmethod
    def created(cls, port: int | str) -> str:
        return f'{_STATUS}:created:{port}'

    @classmethod
    def updated(cls, port: int) -> str:
        return f'{_STATUS}:updated:{port}'

    @classmethod
    def usage(cls, port: int) -> str:
        return f'{_STATUS}:usage:{port}'


class AutoPage:
    """
    用于自动缓存和关闭page
    eg.
    with AutoClosePage(idx, page) as page:
        ...
    """
    __clear_status_lock__ = threading.Lock()

    def __init__(self, port: int, idx: str = None, close: bool = False):
        """
        :param port: 浏览器端口, None表示随机端口
        :param idx: 有idx则会在with后缓存page信息，再次with时会加载进去，None则不会缓存
        :param close: with后是否立即关闭page，默认不立即关，当port=-1时，该参数无效，会强制关闭
        """
        self._port = port
        self._id = idx
        self._close = close
        if (port is None) or (port == -1):
            self._close = True
        self._page = None

        # 未配置定时器自动轮询，暂时为强制关闭
        self._close = True
        pass

    def _semaphore(self) -> Semaphore:
        return Semaphore(f'{_STATUS}-{self._port}')

    @staticmethod
    def _load_page(idx: str, page: ChromiumPage) -> bool:
        cache = REDIS.get(f'{_CACHE}:{cryptotools.md5(idx)}')
        if cache is None:
            return False
        cache = pickle.loads(cache)
        for c in cache['cookies']:
            page.set.cookies(c)
        for k, v in cache['session_storage'].items():
            page.set.session_storage(k, v)
        for k, v in cache['local_storage'].items():
            page.set.local_storage(k, v)
        return True

    @staticmethod
    def _save_page(idx: str, page: ChromiumPage) -> bool:
        return REDIS.set(f'{_CACHE}:{cryptotools.md5(idx)}', pickle.dumps({
            'cookies': page.cookies(all_info=True, all_domains=True),
            'local_storage': page.local_storage(),
            'session_storage': page.session_storage(),
        })) == 1

    @classmethod
    def clear_all_status(cls):
        with cls.__clear_status_lock__:
            key = f'{_STATUS}:*'
            keys = []
            cursor = 0
            while True:
                cursor, partial_keys = REDIS.scan(cursor, match=key)
                keys.extend(partial_keys)
                if cursor == 0:
                    break
            for k in keys:
                REDIS.delete(k)

    @classmethod
    def clear_status(cls, port: int) -> None:
        """
        用于清空已记录的状态
        :param port:
        :return:
        """
        with cls.__clear_status_lock__:
            REDIS.delete(_Key.created(port))
            REDIS.delete(_Key.updated(port))
            REDIS.delete(_Key.usage(port))

    def __enter__(self) -> ChromiumPage:
        with self._semaphore():
            REDIS.set(_Key.created(self._port), time.time(), nx=True)
            REDIS.set(_Key.updated(self._port), time.time())
            REDIS.set(_Key.usage(self._port), 0, nx=True)
            REDIS.incr(_Key.usage(self._port))

            self._page = get_page(self._port)
            if self._id is not None:
                self._load_page(self._id, self._page)

        time.sleep(.5)
        return self._page

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._semaphore():
            if self._id is not None:
                self._save_page(self._id, self._page)

            REDIS.decr(_Key.usage(self._port))

            if self._close:
                self._page.quit()

    def mktab(self) -> ChromiumTab:
        if self._page is None:
            raise ValueError('未开启page!')
        return self._page.new_tab()

    @staticmethod
    def get_created_ports() -> list[int]:
        """
        根据创建时间取已创建端口
        :return:
        """
        key = _Key.created('*')
        keys = []
        cursor = 0
        while True:
            cursor, partial_keys = REDIS.scan(cursor, match=key)
            keys.extend(partial_keys)
            if cursor == 0:
                break
        return [int(x.decode('utf-8').split(':')[-1]) for x in keys]

    @staticmethod
    def get_usage(port: int) -> int | None:
        """
        取该端口的使用数
        :param port:
        :return:
        """
        usage = REDIS.get(_Key.usage(port))
        if usage is None:
            return None
        return int(usage)

    @staticmethod
    def get_updated(port: int) -> float | None:
        """
        获取该端口的最新创建时间
        :param port:
        :return:
        """
        timestamp = REDIS.get(_Key.updated(port))
        if timestamp is None:
            return None
        return float(timestamp)

    @staticmethod
    def get_created(port: int) -> float | None:
        """
        获取该端口的创建时间
        :param port:
        :return:
        """
        timestamp = REDIS.get(_Key.created(port))
        if timestamp is None:
            return None
        return float(timestamp)


class AutoTab:
    """
    用于自动缓存和关闭 tab
    eg.
    with AutoClosePage(idx, page) as page:
        ...
    """

    def __init__(self, port: int = None, idx: str = None, close: bool = False):
        self._port = port
        self._ap = AutoPage(port, idx, close)
        self._tabs: list[ChromiumTab] = []

    def __enter__(self) -> ChromiumTab:
        return self.mktab()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for tab in self._tabs:
            try:
                tab.close()
            except Exception as e:
                logging.warning(f'关闭tab失败, e={e}')
        self._tabs.clear()
        return self._ap.__exit__(exc_type, exc_val, exc_tb)

    def mktab(self) -> ChromiumTab:
        with Semaphore(f'autotab:{self._port}'):
            self._ap.__enter__()
            tab = self._ap.mktab()
            self._tabs.append(tab)
            return tab


AutoPage.clear_all_status()
