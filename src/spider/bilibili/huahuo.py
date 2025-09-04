import datetime
import logging

import requests


def get_report_data(session: requests.Session):
    today = datetime.datetime.now().date()
    min_time = datetime.datetime.combine(today, datetime.time().min)
    min_timestamp = int(min_time.timestamp() * 1000)
    max_time = datetime.datetime.combine(today, datetime.time().max)
    max_timestamp = int(max_time.timestamp() * 1000)
    url = (
        "https://ad.bilibili.com/platform/api/web_api/v1/effect_ad/report/list/by_type"
        f"?campaign_id="
        f"&unit_id="
        f"&creative_id="
        f"&from_time={min_timestamp}"  # 当天00:00:00
        f"&to_time={max_timestamp}"  # 当天23:59:59
        f"&time_type=0"
        f"&launch_type=0"
        f"&deeper_data="
        f"&sort_type="
        f"&sort_field="
        f"&page_size=20"
        f"&page=1"
        f"&size=20"
    )
    payload = {}
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
        'referer': 'https://ad.bilibili.com/',
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
    cost = response_json['result']['data'][0]['cost']
    logging.info(f"bilibili花火的花费为：{cost}")
    return cost
