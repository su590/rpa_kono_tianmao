import logging
import re
import time

import requests
from DrissionPage.items import ChromiumTab

from src.rds.autopage import AutoTab
from src.spider.alud.AludLogin import AludLogin, LoginTag


def _arrive_home_page(tab: ChromiumTab) -> None:
    """
    跳转到首页
    :param tab:
    """
    e_enter_btn = 'c:.bp-entry'
    e_change_org = 'c:.cursor-pointer'
    e_to_home = 'x://div[@mxv="rightViewData"]//span[contains(@class, "fl")]//a[contains(@class, "mr5")]'
    if tab.wait.eles_loaded([e_enter_btn, e_change_org, e_to_home], any_one=True):
        tab.get('https://unidesk.taobao.com/index.html')
        tab.wait.eles_loaded([e_enter_btn, e_change_org, e_to_home], any_one=True, raise_err=True)
    if tab.ele(e_enter_btn):
        tab.ele(e_enter_btn).click()
    if tab.ele(e_change_org):
        return
    url = tab.url
    tab.ele(e_to_home).click()
    tab.wait.url_change(url)
    time.sleep(.5)


def _switch_organization(tab: ChromiumTab, organization: str) -> None:
    """
    切换组织
    :param tab:
    :param organization:
    """
    tab.ele('c:.cursor-pointer').click()
    e_orgs = 'c:label[mxv]'
    tab.wait.ele_displayed(e_orgs)
    org_names: list[str] = [re.sub('[\n\t ]', '', e.text) for e in tab.eles(e_orgs)]
    organization = re.sub('[\n\t ]', '', organization)
    for i, org_name in enumerate(org_names):
        if org_name == organization:
            tab.eles(e_orgs)[i].click()
            time.sleep(.2)
            e_ok = 'c:span[id*="footer_submit"] button'
            tab.ele(e_ok).click()
            tab.wait.ele_deleted(e_ok)
            tab.wait.doc_loaded()
            time.sleep(.5)
            return
    raise ValueError(f'可选组织为: {org_names}, 无法匹配 {organization}')


def _getSession(tab: ChromiumTab, organization: str) -> requests.Session:
    tab.get('https://unidesk.taobao.com/index.html')
    _arrive_home_page(tab)
    _switch_organization(tab, organization)
    e_drop = 'c:.rta-push-btn'
    tab.wait.ele_displayed(e_drop)
    tab.ele(e_drop).click()
    e_to_effect = 'x://li[@title="进入效果首页"]'
    tab.wait.ele_displayed(e_to_effect)
    tab.ele(e_to_effect).click()
    time.sleep(.5)
    tab.wait.doc_loaded()
    e_account = 'x://a[@data-nav="account"]'
    tab.wait.ele_displayed(e_account)
    tab.get(
        f'https://unidesk.taobao.com/direct/index?t={int(time.time() * 1000)}#!/report2/menu/ad?menu=ad&directMediaId='
    )
    tab.wait.doc_loaded()
    cookies = {x['name']: x['value'] for x in tab.cookies(all_domains=True)}
    session = requests.session()
    session.cookies.update(cookies)
    return session


class AludSession:

    @classmethod
    def getSession(cls, username: str, password: str, port: int, organization: str) -> requests.Session:
        """
        获取一份有效session
        基于广告报表面进行获取cookies  https://unidesk.taobao.com/direct/index?t=1733810897599#!/report2/menu/ad?menu=ad&directMediaId=
        :param username:
        :param password:
        :param port:
        :param organization: 所需切换的目标组织
        :return:
        """
        start_time = time.time()
        limit = 3
        for i in range(limit - 1):
            logging.info(f'第{i + 1}次尝试')
            with AutoTab(port) as tab:
                if AludLogin.login(username, password, tab) == LoginTag.SUCCESS:
                    return _getSession(tab, organization)
                tab.clear_cache()
                time.sleep(0.5)
            time.sleep(3)
        logging.info(f'第{limit}次尝试')
        with AutoTab(port) as tab:
            if AludLogin.login(username, password, tab) == LoginTag.SUCCESS:
                return _getSession(tab, organization)
        raise TimeoutError(f'限定{limit}次机会, 总耗时{time.time() - start_time}秒, 未能成功获取到阿里ud的session')
