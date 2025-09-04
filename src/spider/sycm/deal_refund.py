import logging

import requests

from src.utils.trycatchtools import catch_errors


@catch_errors("获取生意参谋成交退款失败")
def get_sscm_deal_refund(session: requests.Session):

    url = "https://sycm.taobao.com/portal/live/new/index/trend/v3.json?dateType=today"

    payload = {}
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.31',
        'priority': 'u=1, i',
        'referer': 'https://sycm.taobao.com/portal/home.htm',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sycm-referer': '/portal/home.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    response = session.request("GET", url, headers=headers, data=payload)
    response_json = response.json()['content']
    deal = response_json['data']['data']['today']['payAmt'][-1]
    refund = response_json['data']['data']['today']['portalShopSucRfdAmt'][-1]
    logging.info(f"生意参谋的成交、退款分别为：{deal}, {refund}")
    return deal, refund