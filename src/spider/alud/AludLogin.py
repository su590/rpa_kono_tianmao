import enum
import random
import time

from DrissionPage.items import ChromiumElement, ChromiumTab

from src.utils.dsptools import dsptools


class LoginTag(enum.Enum):
    SUCCESS = '成功'
    FAIL = '失败'
    SERVER_BUSY = '服务器繁忙'


class AludLogin:
    @classmethod
    def login(cls, username: str, password: str, tab: ChromiumTab) -> LoginTag:
        """
        登录
        :param tab:
        :param username:
        :param password:
        """
        tab.get('https://unidesk.taobao.com/index.html')
        tab.wait.doc_loaded()
        e_topbar = 'c:[mxv="rightViewData"]'
        e_change_org = 'x://span[text()="切换组织"]'
        e_entry = 'c:.bp-entry'
        # e_login_iframe = 'c:login-frame'
        e_id_input: str = '#fm-login-id'
        tab.wait.eles_loaded([e_topbar, e_change_org, e_entry, e_id_input], any_one=True, timeout=10)
        if tab.ele(e_topbar, timeout=1) or tab.ele(e_change_org, timeout=1):
            return LoginTag.SUCCESS
        entry: ChromiumElement = tab.ele(e_entry, timeout=1)
        if entry and entry.states.is_displayed:
            entry.click()
        tab.wait.ele_displayed(e_id_input)
        dsptools.backspace(tab, e_id_input)
        dsptools.typewrite(tab, e_id_input, username)
        time.sleep(.5)
        dsptools.typewrite(tab, '#fm-login-password', password)
        time.sleep(.5)
        login_btn: ChromiumElement = tab.ele('c:.password-login')
        login_btn.click()

        # 检查当前状态
        e_slider = 'c:[aria-label="滑块"]'
        e_server_busy: str = 'x://*[contains(text(), "server is busy")]'
        tab.wait.eles_loaded([e_change_org, e_slider, e_server_busy], any_one=True, raise_err=True)

        # 1.已登录
        if tab.ele(e_change_org):
            return LoginTag.SUCCESS

            # 2.服务器繁忙
        if tab.ele(e_server_busy):
            return LoginTag.SERVER_BUSY

        # 3.滑动验证
        limit: int = 3
        for _ in range(limit):
            tab.wait.ele_displayed('css:[data-nc-lang="SLIDE"]')
            width: float = tab('css:[data-nc-lang="SLIDE"]').rect.size[0]
            actions = tab.actions
            actions.move_to('css:[aria-label="滑块"]')
            actions.hold()
            first: float = random.choice((0.4, 0.5, 0.6))
            actions.right(int(width * first))
            second: float = random.choice((0.1, 0.2, 0.3))
            actions.left(int(width * second))
            third: float = random.choice((0.1, 0.2))
            actions.right(int(width * third))
            fourth: float = 0.1
            actions.left(int(width * fourth))
            left: float = 1 - first + second - third + fourth
            if left > 0.2:
                actions.right(int(width * (left - 0.2)))
            for _ in range(int(width * 0.2)):
                actions.right(1)
                if not login_btn.attr('class').__contains__('fm-button-disabled'):
                    actions.release()
                    login_btn.click()
                    tab.wait.ele_displayed(e_change_org, timeout=10, raise_err=True)
                    return LoginTag.SUCCESS
                iframe = tab.get_frame('#baxia-dialog-content')
                if 'id="`nc_1_refresh1`"' in iframe.html:
                    actions.release()
                    iframe.refresh()
                    time.sleep(1)

        return LoginTag.FAIL
