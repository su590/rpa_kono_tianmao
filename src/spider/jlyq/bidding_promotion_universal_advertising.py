import datetime
import json
import logging
import requests

from src.sql.ktm_message_module import MessageModule
from src.utils.trycatchtools import catch_errors


def _get_bidding_promotion_universal_advertising(session: requests.Session, aadvid: str):
    """
    巨量广告-竞价广告-选择账号
    竞价推广-通投广告
    consumption、gmv、roi
    :return:
    """

    url = f"https://ad.oceanengine.com/superior/api/agw/statistics_sophonx/statQuery?aadvid={aadvid}"

    payload = json.dumps(
        {
            "StartTime": f"{datetime.datetime.combine(datetime.date.today(), datetime.time.min).strftime('%Y-%m-%d %H:%M:%S')}",
            "EndTime": f"{datetime.datetime.combine(datetime.date.today(), datetime.time.max).strftime('%Y-%m-%d %H:%M:%S')}",
            "ComparisonParams": {
                "RatioStartTime": "2025-07-15 00:00:00",
                "RatioEndTime": "2025-07-15 17:00:00"
            },
            "Metrics": [
                "stat_cost",
                "in_app_order_gmv",
                "in_app_order_roi",
                "show_cnt",
                "convert_cnt",
                "cpm_platform",
                "click_cnt",
                "conversion_rate",
                "ctr",
                "cpc_platform",
                "conversion_cost"
            ],
            "DataSetKey": "ad_promotion_basic_data",
            "Filters": {
                "ConditionRelationshipType": 1,
                "Conditions": [
                    {
                        "Field": "campaign_type",
                        "Operator": 7,
                        "Values": [
                            1
                        ]
                    },
                    {
                        "Field": "advertiser_id",
                        "Operator": 7,
                        "Values": [
                            f"{aadvid}"
                        ]
                    }
                ]
            },
            "Dimensions": [
                "stat_time_hour"
            ],
            "PageParams": {
                "Limit": 500,
                "Offset": 0
            },
            "OrderBy": [
                {
                    "Field": "stat_time_hour",
                    "Type": 1
                }
            ],
            "IsDownload": "false",
            "Extra": {
                "is_fill_zero": "true"
            }
        }
    )
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json;charset=UTF-8',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    response = session.request("POST", url, headers=headers, data=payload)
    response_json = response.json()

    # 通投广告数据
    consumption = response_json["data"]["StatsData"]["Totals"]["stat_cost"]["Value"]
    gmv = response_json["data"]["StatsData"]["Totals"]["in_app_order_gmv"]["Value"]
    roi = response_json["data"]["StatsData"]["Totals"]["in_app_order_roi"]["Value"]
    logging.info(f"通投广告的消耗、gmv、roi为：{consumption}, {gmv}, {roi}")
    return consumption, gmv, roi

@catch_errors("巨量引擎经典数据获取失败")
def get_get_bidding_promotion_universal_advertising_classic(session: requests.Session, message_module: MessageModule):
    aadvid = '1833263803089930'
    message_module.ad_classic_consumption, message_module.ad_classic_gmv, message_module.ad_classic_roi = _get_bidding_promotion_universal_advertising(session, aadvid)

@catch_errors("巨量引擎沙龙数据获取失败")
def get_get_bidding_promotion_universal_advertising_salon(session: requests.Session, message_module: MessageModule):
    aadvid = '1833263802617099'
    message_module.ad_solon_consumption, message_module.ad_solon_gmv, message_module.ad_solon_roi = _get_bidding_promotion_universal_advertising(session, aadvid)



