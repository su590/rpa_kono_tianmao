# -*- coding: utf-8 -*-  
"""
服务于DrssionPage的工具包
使用前需要先安装DrissionPage
"""
import logging
import random
import subprocess
import time
import traceback
from typing import Callable, Union, Optional

from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.common import Keys
from DrissionPage.errors import PageDisconnectedError, BrowserConnectError
from DrissionPage.items import ChromiumElement, ChromiumFrame, ChromiumTab

_logger = logging.getLogger('dsptools')


class DspTools:
    _BROWSER_PATH: Optional[str] = "chrome"

    @classmethod
    def path(cls) -> str:
        """
        取浏览器地址，默认来自where chrome
        :return:
        """
        if cls._BROWSER_PATH is None:
            cls._BROWSER_PATH = subprocess.check_output("where chrome", shell=True, text=True).strip()
        return cls._BROWSER_PATH

    @classmethod
    def setpath(cls, path: str) -> None:
        """
        自定义修改浏览器地址
        :param path: 浏览器地址的绝对地址
        :return:
        """
        cls._BROWSER_PATH = path

    @classmethod
    def options(cls) -> ChromiumOptions:
        """
        获取一份默认的浏览器配置
        :return:
        """
        co: ChromiumOptions = ChromiumOptions(read_file=False)

        # 窗口最大化
        co.set_argument('--start-maximized')
        # 禁用默认浏览器检查
        co.set_argument('--no-default-browser-check')
        # 禁用地址栏的建议功能
        co.set_argument('--disable-suggestions-ui')
        # 禁用“首次运行”的欢迎页面和配置向导
        co.set_argument('--no-first-run')
        # 禁用浏览器的提示信息栏，如提示用户保存密码
        co.set_argument('--disable-infobars')
        # 禁用浏览器的弹窗阻止功能
        co.set_argument('--disable-popup-blocking')
        # 隐藏崩溃恢复提示气泡
        co.set_argument('--hide-crash-restore-bubble')
        # 禁用隐私沙箱（Privacy Sandbox）设置中的某个特定功能，即 "PrivacySandboxSettings4"
        co.set_argument('--disable-features=PrivacySandboxSettings4')

        # 设置浏览器exe地址
        co.set_paths(browser_path=cls.path())
        return co

    @staticmethod
    def local_expand(
            *,
            port: int = None, download_path: str = None, user_data_path: str = None, ip: str = '127.0.0.1',
    ) -> Callable[[ChromiumOptions], ChromiumOptions]:
        """
        返回一个函数，该函数可返回内容为"基于默认浏览器配置，获取一份设定了多项本地化设置的浏览器配置"

        举例: chromium_options_func(port=9222, download_path='D:/reptile/download', user_data_path='D:/reptile/chromes/9222', ip='127.0.0.1')

        :param port: 指定浏览器端口，如9222
        :param download_path: 指定默认下载地址
        :param user_data_path: 指定用户文件夹路径
        :param ip: 指定浏览器代理ip，默认127.0.0.1
        """

        def local_cofunc(co: ChromiumOptions) -> ChromiumOptions:
            if port:
                co.set_paths(address=f'{ip}:{port}')
            if download_path:
                co.set_paths(download_path=download_path)
            if user_data_path:
                co.set_paths(user_data_path=user_data_path)
            return co

        return local_cofunc

    @classmethod
    def page(cls, expand: Callable[[ChromiumOptions], ChromiumOptions] = None,
             scope: tuple[int, int] = None) -> ChromiumPage:
        """
        基于默认的浏览器配置，获取一份浏览器窗口
        :param expand: 拓展浏览器配置选项，默认时会附加一次随机端口
        :param scope: 自定义默认的随机端口的端口选择范围
        """
        co = cls.options()
        if expand is None:
            co.auto_port(scope=scope)
        else:
            co = expand(co)
        timeout = 3
        cp = None
        err = None
        while timeout > 0:
            try:
                cp = ChromiumPage(addr_or_opts=co)
            except (PageDisconnectedError, BrowserConnectError) as e:
                _logger.warning(f'启动浏览器异常: e={e}\n{traceback.format_exc()}')
                timeout -= 1
                err = e
            else:
                break
        if cp:
            return cp
        raise err

    @classmethod
    def typewrite(
            cls,
            page: Union[ChromiumPage, ChromiumFrame, ChromiumTab],
            locator: Union[str, tuple[str, str], ChromiumElement],
            text: str,
    ) -> None:
        """
        打字，即缓慢输入
        示例 typewrite(page, '#fm-login-id', 'account')
        :param page: ChromiumPage
        :param locator: 元素定位
        :param text: 输入文本
        :return:
        """
        actions = page.actions.click(locator)
        for c in text:
            actions.type(c)
            time.sleep(random.uniform(0.1, 0.2))

    @staticmethod
    def property_value(
            page: Union[ChromiumPage, ChromiumFrame, ChromiumTab],
            locator: str,
            timeout: float = 1.5,
    ) -> str:
        """
        用于取文本框的文本内容

        :param page: 操作窗口
        :param locator: 元素定位
        :param timeout: 取值限时
        """
        start = time.time()
        page.wait.doc_loaded()
        page.wait.ele_displayed(locator)
        time.sleep(random.uniform(0.1, 0.2))
        value = page.ele(locator).property('value')
        timeout -= time.time() - start
        while value == '' and timeout > 0:
            sleep = random.uniform(0.1, 0.2)
            time.sleep(sleep)
            value = page.ele(locator).property('value')
            timeout -= sleep
        return value

    pv = property_value

    @classmethod
    def backspace(
            cls,
            page: Union[ChromiumPage, ChromiumFrame, ChromiumTab],
            locator: str,
    ) -> None:
        """
        逐个删除文本框字符
        :param page: ChromiumPage, 其实应该是ChromiumBase
        :param locator: 元素定位
        """
        count = len(cls.pv(page, locator))
        ac = page.actions
        ac.click(locator)
        for _ in range(count):
            ac.type(Keys.RIGHT)
            ac.type(Keys.BACKSPACE)

    @staticmethod
    def ele(page: ChromiumPage, *locators: str) -> ChromiumElement:
        """
        层级查找元素并返回
        使用举例： ele(page, '#fm-login-id', 'c:input')，效果等同于 page('#fm-login-id')('c:input')
        :param page: 操作窗口
        :param locators: 定位
        :return:
        """
        assert locators, '定位不应为空'
        element = page
        for locator in locators:
            element = element(locator)
        return element

    @classmethod
    def pierce(cls, page: Union[ChromiumPage, ChromiumTab], *locators: str) -> None:
        """
        击穿，即删除所有遮挡在目标元素之前的元素
        使用举例： pierce(page, '#fm-login-id', 'c:input')
        :param page: 操作窗口
        :param locators: 定位
        :return:
        """
        element: ChromiumElement = cls.ele(page, *locators)
        while element.states.is_covered:
            node: dict = element.owner.run_cdp(
                cmd='DOM.describeNode',
                backendNodeId=element.states.is_covered
            ).get('node')
            css: str = f"{node['nodeName']}"
            for i in range(0, len(node.get('attributes', [])), 2):
                css += f"[{node['attributes'][i]}='{node['attributes'][i + 1]}']"
            page.remove_ele(f'c:{css}')


dsptools = DspTools
