# -*- coding: utf-8 -*-  
"""
@Date     : 2024-12-05
@Author   : xwq
@Desc     : <None>

"""
import requests

from src.rds.autopage import AutoTab
from src.spider.sycm.SycmLogin import SycmLogin


class SycmSession:
    """
    生意参谋 - session
    来自首页
    """

    @classmethod
    def getSession(cls, username: str, password: str, port: int) -> requests.Session:
        """
        获取一份有效session
        基于商品排行页面进行获取cookies  https://sycm.taobao.com/cc/item_rank
        :param username:
        :param password:
        :param port:
        :return:
        """
        with AutoTab(port) as tab:
            SycmLogin.login(username, password, tab)
            tab.get('https://sycm.taobao.com/cc/item_rank')
            tab.wait.doc_loaded()
            cookies = {x['name']: x['value'] for x in tab.cookies(all_domains=True)}
            session = requests.session()
            session.cookies.update(cookies)
            return session
