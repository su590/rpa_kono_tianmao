# -*- coding: utf-8 -*-
"""
@Date     : 2024-12-24
@Author   : xwq
@Desc     : <None>

"""
import time

import requests
from DrissionPage.items import ChromiumTab

from src.spider.wph.WphTools import verify
from src.utils.dsptools import dsptools
from src.utils.logintools import Login, Session
from src.utils.tabtools import EasyTab


def _is_login(tab: ChromiumTab) -> bool:
    tab.listen.start('https://vc-auth.vip.com/vc/vcMenuService/getVisMenu')
    tab.get(f'https://vis.vip.com/#/app-v/vis-vue-new/index?t={int(time.time() * 1000)}')
    dp = tab.listen.wait(timeout=10)
    return bool(dp)


def _open_login_url(tab: ChromiumTab):
    url = 'https://vis.vip.com/login.php'
    if not tab.url.startswith(url):
        tab.get(url)
        tab.wait.doc_loaded()
        time.sleep(.5)


def _login(username: str, password: str, tab: ChromiumTab) -> None:
    _open_login_url(tab)

    # 账密登录
    e_acc_login: str = 'x://span[text()="账户登录"]'
    tab.ele(e_acc_login).click()
    e_user_input: str = 'c:[id="J_login_name"]'
    dsptools.typewrite(tab, e_user_input, username)
    e_password_input: str = 'c:[id="J_login_pwd"]'
    dsptools.typewrite(tab, e_password_input, password)
    e_i_agree: str = 'x://input[@id="J_login_agree"]/../label'
    tab.ele(e_i_agree).click()
    login_button: str = 'c:[id="J_login_submit"]'
    tab.ele(login_button).click()

    # 点选验证
    verify(tab, 10)
    tab.listen.start('https://vc-gw.vip.com/vendor/getVendorOverviewByAccount')
    tab.ele(login_button).click()
    tab.listen.wait(timeout=20, raise_err=True)
    time.sleep(.5)


class WphGysLogin(Login):
    def __init__(self, username: str, password: str, port: int):
        super().__init__(port, username)
        self._password = password

    def _login(self, tab: ChromiumTab) -> None:
        if _is_login(tab):
            time.sleep(.5)
            return
        _login(self._username, self._password, tab)
        time.sleep(.5)

class WphGysSession(Session):
    def __init__(self, username: str, password: str, port: int):
        super().__init__(port, username)
        self._password = password

    def _session(self) -> requests.Session:
        with WphGysLogin(self._username, self._password, self._port) as tab:
            time.sleep(1)
            tab.get('https://compass.vip.com/frontend/index.html#/homepage')
            return EasyTab(tab).session('https://compass.vip.com/frontend/index.html#/industry/productList')


