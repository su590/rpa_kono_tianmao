import concurrent
import os
import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import requests
from DrissionPage.errors import WaitTimeoutError
from DrissionPage.items import ChromiumFrame, ChromiumTab

from src.config import COMMON_DOWNLOAD_PATH
from src.utils.dsptools import dsptools


class EasyTab:
    def __init__(self, tab: ChromiumTab | ChromiumFrame):
        self._tab = tab

    def get(self, url: str):
        tab = self._tab
        tab.wait.doc_loaded()
        if tab.url.rstrip('/') != url:
            tab.get(url)
            tab.wait.doc_loaded()

    def click(self, ele: str, pierce: bool = False):
        tab = self._tab
        tab.wait.ele_displayed(ele, raise_err=True, timeout=10)
        time.sleep(random.uniform(0.2, 0.3))
        if pierce and tab.ele(ele).states.is_covered:
            dsptools.pierce(tab, ele)
            time.sleep(.5)
        tab.actions.move_to(self.point(ele)).click()

    def wait(self, ele: str, timeout: int = 10, raise_err: bool = True):
        tab = self._tab
        tab.wait.eles_loaded(ele, raise_err=raise_err, timeout=timeout)
        tab.wait.ele_displayed(ele, raise_err=raise_err, timeout=timeout)

    def input(self, ele: str, text: str):
        self.click(ele)
        dsptools.backspace(self._tab, ele)
        dsptools.typewrite(self._tab, ele, text)

    def screenshot(self, ele: str, path: str = None) -> str:
        tab = self._tab
        tab.wait.ele_displayed(ele, raise_err=True, timeout=10)
        time.sleep(.5)
        if path is None:
            path = os.path.join(COMMON_DOWNLOAD_PATH, f'{str(uuid.uuid4())}.png')
        tab.ele(ele).get_screenshot(path)
        return path

    def location(self, ele: str) -> tuple[int, int]:
        tab = self._tab
        tab.wait.ele_displayed(ele, raise_err=True, timeout=10)
        x = tab.ele(ele).rect.location
        return int(x[0]), int(x[1])

    def size(self, ele: str) -> tuple[int, int]:
        tab = self._tab
        tab.wait.ele_displayed(ele, raise_err=True, timeout=10)
        s = tab.ele(ele).rect.size
        return int(s[0]), int(s[1])

    def point(self, ele: str) -> tuple[int, int]:
        x, y = self.location(ele)
        w, h = self.size(ele)
        return x + w // 2, y + h // 2

    @classmethod
    def add(cls, a: tuple[float, float], b: tuple[float, float]) -> tuple[int, int]:
        return int(a[0] + b[0]), int(a[1] + b[1])

    def slide(
            self,
            ele: str,
            offset: int,
            y_scope: int = None,
            x_scope: float = 0.3,
            duration: float = 1.5
    ):
        if y_scope is None:
            y_scope = self.size(ele)[1]
        y_scope //= 2
        duration = max(1.5, duration)
        start = self.point(ele)

        ac = self._tab.actions
        ac.move_to(start).hold()
        ac.move_to(self.add(start, (offset * 0.1, random.randint(-y_scope, y_scope))), duration * 0.2)
        ac.move_to(
            self.add(start, (offset * (1 + random.uniform(x_scope / 2, x_scope)), random.randint(-y_scope, y_scope))),
            duration * 0.1
        )
        ac.move_to(self.add(start, (offset * (1 - random.uniform(0.2, 0.3)), random.randint(-y_scope, y_scope))),
                   duration * 0.3)
        ac.move_to(self.add(start, (offset, random.randint(-y_scope, y_scope))), duration * 0.4)
        ac.release()

    def session(self, url: str = None, all_info: bool = None, all_domains: bool = None) -> requests.Session:
        if url is not None:
            self.get(url)
        kwargs = {}
        if all_info is not None:
            kwargs['all_info'] = all_info
        if all_domains is not None:
            kwargs['all_domains'] = all_domains
        cookies = {x['name']: x['value'] for x in self._tab.cookies(**kwargs)}
        session = requests.session()
        session.cookies.update(cookies)
        return session

    def catch(self, ele: str, url: str) -> dict:
        """
        抓取: 点击, 并监听某个报文响应
        """
        tab = self._tab
        tab.listen.start(url)
        self.click(ele)
        dp = tab.listen.wait(timeout=10, raise_err=True)
        body = dp.response.body
        tab.listen.stop()
        return body


def wait_any_ele_displayed(tab: ChromiumTab, eles: list[str], timeout: int = 10, raise_err: bool = False) -> str | None:
    """
    等待任一元素可见（基于线程池）
    :param tab: ChromiumTab实例
    :param eles: 元素选择器列表
    :param timeout: 单个元素等待超时时间
    :param raise_err: 不满足时是否报错
    :return: 第一个显示的元素选择器，若无则返回None
    """
    max_workers = len(eles)
    if max_workers == 0:
        raise ValueError('eles不应为空')
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(tab.wait.ele_displayed, loc_or_ele=ele, timeout=timeout, raise_err=False): ele
            for ele in eles
        }
        for future in concurrent.futures.as_completed(futures.keys()):
            if future.result():
                for f in futures:
                    if not f.done():
                        f.cancel()
                return futures[future]
    if raise_err:
        raise WaitTimeoutError('等待{}失败（等待{}秒）。', '元素显示', timeout)
    else:
        return None
