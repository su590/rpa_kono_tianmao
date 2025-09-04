import datetime
import logging
import requests

from src.sql.ktm_message_module import MessageModule
from src.utils.trycatchtools import catch_errors


def _get_account_statement(session: requests.Session, advertiser_id: str, effect: int):

    url = (
        "https://unidesk.taobao.com/api/direct/mix/report/basic/summary"
        "?r=mx_617"
        "&advType=1"
        "&customerType=2"
        "&directMediaId=103"
        f"&effect={effect}"
        "&effectType=click"
        "&ef=hourId"
        f"&startTime={datetime.datetime.now().strftime('%Y-%m-%d')}"
        f"&endTime={datetime.datetime.now().strftime('%Y-%m-%d')}"
        "&bizType=37"
        "&mapiVersion=1"
        f"&advertiserId={advertiser_id}"
        "&top=5"
    )
    payload = {}
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.31',
        'priority': 'u=1, i',
        'referer': 'https://unidesk.taobao.com/direct/index',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    response = session.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    data = response_json['data']['summary']
    cost = data['cost'] / 100
    transaction_amount = data['transactionAmount'] / 100
    return_on_investment = round(data['returnOnInvestment'], 2)
    ad_pv = data['adPv']
    cost_per_mail = round(data['ecpm'] / 100, 2)
    favorite_baby_volume = data['favoriteBabyVolume']
    add_cart_volume = data['addCartVolume']
    logging.info(f"在阿里ud下以{effect}天计算的消耗、成交订单金额、投资回报率、展现量、千次展现成本、收藏宝贝量、添加购物车量为: {cost}, {transaction_amount}, {return_on_investment},"
                 f"{ad_pv}, {cost_per_mail}, {favorite_baby_volume}, {add_cart_volume} ")
    return cost, transaction_amount, return_on_investment, ad_pv, cost_per_mail, favorite_baby_volume, add_cart_volume

@catch_errors("阿里ud下上海网道广告有限公司-效果数据获取失败")
def get_effect_account_statement(session: requests.Session, message_module: MessageModule):
    """
    获取 上海网道广告有限公司-效果 账号下的信息
    :param session:
    :return:
    """
    advertiser_id = "6894361"
    (message_module.ud_cost_one,
     message_module.ud_transaction_amount_one,
     message_module.ud_return_on_investment_one,
     message_module.ud_ad_pv_one,
     message_module.ud_cost_per_mille_one,
     message_module.ud_favorite_baby_volume_one,
     message_module.ud_add_cart_volume_one) = _get_account_statement(session, advertiser_id, 1)

    (message_module.ud_cost_seven,
     message_module.ud_transaction_amount_seven,
     message_module.ud_return_on_investment_seven,
     message_module.ud_ad_pv_seven,
     message_module.ud_cost_per_mille_seven,
     message_module.ud_favorite_baby_volume_seven,
     message_module.ud_add_cart_volume_seven) = _get_account_statement(session, advertiser_id, 7)

@catch_errors("阿里ud下海网道广告有限公司UDPLUS - 效果Plus数据获取失败")
def get_effect_plus_account_statement_number_eleven(session: requests.Session, message_module: MessageModule):
    """
    获取 上海网道广告有限公司UDPLUS - 效果Plus 账号下的信息
    :param session:
    :return:
    """
    advertiser_id = "1017277"
    (message_module.ud_plus_cost_one,
     message_module.ud_plus_transaction_amount_one,
     message_module.ud_plus_return_on_investment_one,
     message_module.ud_plus_ad_pv_one,
     message_module.ud_plus_cost_per_mille_one,
     message_module.ud_plus_favorite_baby_volume_one,
     message_module.ud_plus_add_cart_volume_one) = _get_account_statement(session, advertiser_id, 1)

    (message_module.ud_plus_cost_fifteen,
     message_module.ud_plus_transaction_amount_fifteen,
     message_module.ud_plus_return_on_investment_fifteen,
     message_module.ud_plus_ad_pv_fifteen,
     message_module.ud_plus_cost_per_mille_fifteen,
     message_module.ud_plus_favorite_baby_volume_fifteen,
     message_module.ud_plus_add_cart_volume_fifteen) = _get_account_statement(session, advertiser_id, 15)

@catch_errors("阿里ud下海网道广告有限公司UDPLUS - 效果Plus数据获取失败")
def get_effect_plus_account_statement_number_one(session: requests.Session, message_module: MessageModule):
    """
    获取 上海网道广告有限公司UDPLUS - 效果Plus 账号下的信息
    :param session:
    :return:
    """
    advertiser_id = "311780"
    (message_module.ud_plus_cost_one_number_one,
     message_module.ud_plus_transaction_amount_one_number_one,
     message_module.ud_plus_return_on_investment_one_number_one,
     message_module.ud_plus_ad_pv_one_number_one,
     message_module.ud_plus_cost_per_mille_one_number_one,
     message_module.ud_plus_favorite_baby_volume_one_number_one,
     message_module.ud_plus_add_cart_volume_one_number_one) = _get_account_statement(session, advertiser_id, 1)

    (message_module.ud_plus_cost_fifteen_number_one,
     message_module.ud_plus_transaction_amount_fifteen_number_one,
     message_module.ud_plus_return_on_investment_fifteen_number_one,
     message_module.ud_plus_ad_pv_fifteen_number_one,
     message_module.ud_plus_cost_per_mille_fifteen_number_one,
     message_module.ud_plus_favorite_baby_volume_fifteen_number_one,
     message_module.ud_plus_add_cart_volume_fifteen_number_one) = _get_account_statement(session, advertiser_id, 15)




