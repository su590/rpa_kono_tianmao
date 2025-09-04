import datetime
import logging
import re
import time

from DrissionPage.errors import WaitTimeoutError
from DrissionPage.items import ChromiumTab

from src.utils.dsptools import dsptools
from src.utils.smstools import wait_sms
from src.utils.tabtools import EasyTab

def _isLogined(tab: ChromiumTab) -> bool:
    """
    是否已登录
    :param tab:
    :return:
    """
    tab.listen.start('https://sycm.taobao.com/custom/menu/getPersonalView.json')
    tab.get('https://sycm.taobao.com/portal/home.htm')
    dp = tab.listen.wait(timeout=10)
    if dp and dp.response.body['code'] == 0:
        return True
    else:
        return False

# 账号对应的验证手机号
PHONE_NUMBER = '19120687280'

class SycmLogin:
    """
    生意参谋 - 登录
    https://sycm.taobao.com/custom/login.htm?_target=http://sycm.taobao.com/portal/home.htm
    """

    @classmethod
    def login(cls, username: str, password: str, tab: ChromiumTab) -> None:
        _start_time = datetime.datetime.now()
        logging.info(f'开始登录生意参谋: {_start_time}')

        if _isLogined(tab):
            return

        tab.get('https://sycm.taobao.com/custom/login.htm?_target=http://sycm.taobao.com/portal/home.htm')
        tab.wait.doc_loaded()
        e_username_input = 'c:[placeholder="账号名/邮箱/手机号"]'
        tab.wait.ele_displayed(e_username_input)
        dsptools.typewrite(tab, e_username_input, username)
        e_password_input = 'c:[placeholder="请输入登录密码"]'
        tab.wait.ele_displayed(e_password_input)
        tab.listen.start('https://sycm.taobao.com/custom/menu/getPersonalView.json')
        dsptools.typewrite(tab, e_password_input, f'{password}\n')
        try:
            tab.listen.wait(timeout=10, raise_err=True)
        except WaitTimeoutError:
            # 在这接入短信的服务
            et = EasyTab(tab)

            before_send = datetime.datetime.now()
            et.click('x://button[@id="J_GetCode"]')

            start_time = time.time()
            after_time = before_send
            timeout = 60 * 30
            true_code = False
            while time.time() - start_time <= timeout:
                # 取验证码
                smss = wait_sms(PHONE_NUMBER, after_time, 100, '【阿里巴巴】验证码', timeout)
                codes: list[str] = []
                for sms in smss:
                    possibles = re.findall('【阿里巴巴】验证码(\d+)', sms.message)
                    if len(possibles) > 0:
                        codes.append(possibles[0])

                # 更新时间
                after_time = smss[0].date

                # 依次尝试
                for code in codes:
                    tab.listen.start('https://acjs.aliyun.com/error', method='GET')
                    et.input('x://input[@id="J_Checkcode"]', code)
                    et.click('x://button[@id="btn-submit"]')
                    dp = tab.listen.wait(timeout=10)
                    if not dp:
                        continue
                    is_failed = dp.is_failed
                    tab.listen.stop()
                    if not is_failed:
                        true_code = True
                        break

                if true_code:
                    break

        tab.wait.doc_loaded()
        time.sleep(.5)
        _end_time = datetime.datetime.now()
        logging.info(f'完成登录生意参谋: {_end_time}, 耗时: {_end_time - _start_time}')
