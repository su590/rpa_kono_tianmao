import dataclasses
import json
import os.path
import time
import datetime

from DrissionPage._pages.chromium_page import ChromiumPage

from src.schedule import PATH
from src.spider.alud.AludSession import AludSession
from src.spider.alud.account_statement import get_effect_account_statement, get_effect_plus_account_statement_number_eleven, get_effect_plus_account_statement_number_one
from src.spider.bilibili.huahuo import get_report_data
from src.spider.jlyq.bidding_promotion_universal_advertising import get_get_bidding_promotion_universal_advertising_classic, get_get_bidding_promotion_universal_advertising_salon
from src.spider.jlyq.jlyq_session import JlyqSession
from src.spider.sycm.SycmSession import SycmSession
from src.spider.sycm.deal_refund import get_sscm_deal_refund
from src.spider.sycm.ud_effect_placement import get_ud_effect_placement
from src.sql.ktm_message_module import MessageModule
from src.utils.feishutools import send_message_by_robot, insert_spread_append, insert_spread_cover
from src.utils.tabtools import EasyTab
from src.utils.trycatchtools import catch_errors

SPREAD_SHEET_TOKEN = 'XruNsWfTShegEXtqwD2cLxl1noc'
SHEET_TOKEN_NOW = '0jiSmW'
SHEET_TOKEN_HISTORY = '1eFHlh'

# 账号基类
@dataclasses.dataclass
class _Account:
    username: str
    password: str
    port: int

# 巨量引擎账户信息
@dataclasses.dataclass
class _JlyqAccount(_Account):
    pass

# 生意参谋账户信息
@dataclasses.dataclass
class _SycmAccount(_Account):
    pass

# 阿里ud账户信息
@dataclasses.dataclass
class _ALUDAccount(_Account):
    organization: str

def _get_jlyq_account() -> _JlyqAccount:
    path = os.path.join(PATH, 'jlyq_account.json')
    with open(path, 'r', encoding='utf-8') as f:
        account_dict: dict = json.load(f)[0]
        return _JlyqAccount(**account_dict)

def _get_sycm_account() -> _SycmAccount:
    path = os.path.join(PATH, 'sycm_account.json')
    with open(path, 'r', encoding='utf-8') as f:
        account_dict: dict = json.load(f)[0]
        return _SycmAccount(**account_dict)

def _get_alud_account(index: int) -> _ALUDAccount:
    """
    获取阿里ud 账户信息
    :param index: 数组当中的第几个
    :return:
    """
    path = os.path.join(PATH, 'alud_account.json')
    with open(path, 'r', encoding='utf-8') as f:
        account_dict: dict = json.load(f)[index]
        return _ALUDAccount(**account_dict)

@catch_errors("巨量引擎数据获取失败")
def _jlyq_data(_jlyq_account: _JlyqAccount, _message_module: MessageModule):
    """
    获取巨量引擎数据
    :param _jlyq_account: 巨量引擎账号信息
    :return:
    """
    with JlyqSession(_jlyq_account.port, _jlyq_account.username, _jlyq_account.password) as session:
        get_get_bidding_promotion_universal_advertising_classic(session, _message_module)
        get_get_bidding_promotion_universal_advertising_salon(session, _message_module)

@catch_errors("生意参谋数据获取失败")
def _sycm_data(_sycm_account: _SycmAccount, _message_module: MessageModule):
    """
    获取生意参谋数据
    :param _sycm_account: 生意参谋账号信息
    :return:
    """
    session = SycmSession.getSession(_sycm_account.username, _sycm_account.password, _sycm_account.port)
    _message_module.ud_visitor_number = get_ud_effect_placement(session)
    _message_module.sycm_pay, _message_module.sycm_refund = get_sscm_deal_refund(session)

@catch_errors("阿里ud数据获取失败")
def _alud_data(_message_module: MessageModule):
    """
    获取阿里ud的数据
    :return:
    """
    effect_account = _get_alud_account(0)
    effect_session = AludSession.getSession(effect_account.username, effect_account.password, effect_account.port, effect_account.organization)
    get_effect_account_statement(effect_session, _message_module)
    time.sleep(5)
    effect_plus_account = _get_alud_account(1)
    effect_plus_session = AludSession.getSession(effect_plus_account.username, effect_plus_account.password, effect_plus_account.port, effect_plus_account.organization)
    get_effect_plus_account_statement_number_eleven(effect_plus_session, _message_module)
    get_effect_plus_account_statement_number_one(effect_plus_session, _message_module)

def _assemble_feishu_message(_message_module: MessageModule):
    text = f"消息推送展示项目：KONO天猫站外投放实时数据\n" \
           f">> 日期：{datetime.datetime.now().strftime('%y:%m:%d')}" \
           f">> 获取时间：{datetime.datetime.now().strftime('%H:%M:%S')};\n" \
           "【流量看板】\n" \
           f">> UD访客数：{_message_module.ud_visitor_number};\n" \
           "【生意参谋】\n" \
           f">> 成交：{_message_module.sycm_pay}; \n" \
           f">> 退款：{_message_module.sycm_refund}; \n"\
           "【UD新户数据：一天】\n" \
           f">> 消耗：{_message_module.ud_cost_one};\n" \
           f">> 成交订单金额：{_message_module.ud_transaction_amount_one};\n" \
           f">> 投资回报率：{_message_module.ud_return_on_investment_one};\n" \
           f">> 展现量：{_message_module.ud_ad_pv_one};\n" \
           f">> 千次展现成本：{_message_module.ud_cost_per_mille_one};\n" \
           f">> 收藏宝贝量：{_message_module.ud_favorite_baby_volume_one};\n" \
           f">> 添加购物车量：{_message_module.ud_add_cart_volume_one};\n" \
           "【UD新户数据：七天】\n" \
           f">> 消耗：{_message_module.ud_cost_seven};\n" \
           f">> 成交订单金额：{_message_module.ud_transaction_amount_seven};\n" \
           f">> 投资回报率：{_message_module.ud_return_on_investment_seven};\n" \
           f">> 展现量：{_message_module.ud_ad_pv_seven};\n" \
           f">> 千次展现成本：{_message_module.ud_cost_per_mille_seven};\n" \
           f">> 收藏宝贝量：{_message_module.ud_favorite_baby_volume_seven};\n" \
           f">> 添加购物车量：{_message_module.ud_add_cart_volume_seven};\n" \
           "【UD数据（十一号）：一天】\n" \
           f">> 消耗：{_message_module.ud_plus_cost_one};\n" \
           f">> 成交订单金额：{_message_module.ud_plus_transaction_amount_one};\n" \
           f">> 投资回报率：{_message_module.ud_plus_return_on_investment_one};\n" \
           f">> 展现量：{_message_module.ud_plus_ad_pv_one};\n" \
           f">> 千次展现成本：{_message_module.ud_plus_cost_per_mille_one};\n" \
           f">> 收藏宝贝量：{_message_module.ud_plus_favorite_baby_volume_one};\n" \
           f">> 添加购物车量：{_message_module.ud_plus_add_cart_volume_one};\n" \
           "【UD数据（十一号）：十五天】\n" \
           f">> 消耗：{_message_module.ud_plus_cost_fifteen};\n" \
           f">> 成交订单金额：{_message_module.ud_plus_transaction_amount_fifteen};\n" \
           f">> 投资回报率：{_message_module.ud_plus_return_on_investment_fifteen};\n" \
           f">> 展现量：{_message_module.ud_plus_ad_pv_fifteen};\n" \
           f">> 千次展现成本：{_message_module.ud_plus_cost_per_mille_fifteen};\n" \
           f">> 收藏宝贝量：{_message_module.ud_plus_favorite_baby_volume_fifteen};\n" \
           f">> 添加购物车量：{_message_module.ud_plus_add_cart_volume_fifteen};\n" \
           "【UD数据（一号）：一天】\n" \
           f">> 消耗：{_message_module.ud_plus_cost_one_number_one};\n" \
           f">> 成交订单金额：{_message_module.ud_plus_transaction_amount_one_number_one};\n" \
           f">> 投资回报率：{_message_module.ud_plus_return_on_investment_one_number_one};\n" \
           f">> 展现量：{_message_module.ud_plus_ad_pv_one_number_one};\n" \
           f">> 千次展现成本：{_message_module.ud_plus_cost_per_mille_one_number_one};\n" \
           f">> 收藏宝贝量：{_message_module.ud_plus_favorite_baby_volume_one_number_one};\n" \
           f">> 添加购物车量：{_message_module.ud_plus_add_cart_volume_one_number_one};\n" \
           "【UD数据（一号）：十五天】\n" \
           f">> 消耗：{_message_module.ud_plus_cost_fifteen_number_one};\n" \
           f">> 成交订单金额：{_message_module.ud_plus_transaction_amount_fifteen_number_one};\n" \
           f">> 投资回报率：{_message_module.ud_plus_return_on_investment_fifteen_number_one};\n" \
           f">> 展现量：{_message_module.ud_plus_ad_pv_fifteen_number_one};\n" \
           f">> 千次展现成本：{_message_module.ud_plus_cost_per_mille_fifteen_number_one};\n" \
           f">> 收藏宝贝量：{_message_module.ud_plus_favorite_baby_volume_fifteen_number_one};\n" \
           f">> 添加购物车量：{_message_module.ud_plus_add_cart_volume_fifteen_number_one};\n" \
           "【AD经典数据】\n" \
           f">> 消耗：{_message_module.ad_classic_consumption};\n" \
           f">> GMV：{_message_module.ad_classic_gmv}; \n" \
           f">> ROI：{_message_module.ad_classic_roi}; \n" \
           "【AD沙龙数据】\n" \
           f">> 消耗：{_message_module.ad_solon_consumption};\n" \
           f">> GMV：{_message_module.ad_solon_gmv}; \n" \
           f">> ROI：{_message_module.ad_solon_roi}; \n" \
           "【B站数据】\n" \
           f">> 总花费：{_message_module.bilibili_cost}; \n"

    return text

def _assemble_sheet_list(_message_module: MessageModule):
    _list = [f"{datetime.datetime.now().strftime('%Y:%m:%d')}",
             f"{datetime.datetime.now().strftime('%H:%M:%S')}"]
    _list.extend(dataclasses.astuple(_message_module))
    return _list

@catch_errors("bilibili花火数据获取失败")
def _bilibili_hua_huo_data(_message_module: MessageModule):
    """
    获取bilibili花火的数据
    默认是登录的，如果登录状态过期需要手动进行调整
    :return:
    """
    page = ChromiumPage(9603)
    session = EasyTab(page.latest_tab).session("https://huahuo.bilibili.com/#/home/index?customer=undefined")
    _message_module.bilibili_cost = get_report_data(session)
    page.close()

def run_kono_tianmao():
    # 初始化消息类
    message_module = MessageModule()
    # 飞书机器人链接
    ROBOT_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/e33e32d9-7499-4aaf-8618-ef07be46b48d"

    _jlyq_data(_get_jlyq_account(), message_module)
    _sycm_data(_get_sycm_account(), message_module)
    _alud_data(message_module)
    _bilibili_hua_huo_data(message_module)
    send_message_by_robot(_assemble_feishu_message(message_module), ROBOT_URL)

    _list = _assemble_sheet_list(message_module)
    insert_spread_append(SPREAD_SHEET_TOKEN, SHEET_TOKEN_HISTORY, _list)
    _list.insert(0, '今日时段数据')
    insert_spread_cover(SPREAD_SHEET_TOKEN, SHEET_TOKEN_NOW, _list, 3)

if __name__ == '__main__':
    run_kono_tianmao()

