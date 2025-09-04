import datetime
import logging
from urllib.parse import quote
import requests


def get_ud_effect_placement(session: requests.Session):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    raw_value = f"{today}|{today}"
    encoded_value = quote(raw_value)
    url = (
        "https://sycm.taobao.com/flow/overview/live/shopFlowSourceTop/v4.json"
        f"?dateRange={encoded_value}"
        "&dateType=today"
        "&pageSize=10"  
        "&page=1"  
        "&order=desc" 
        "&orderBy=uv" 
        "&flowBizType=all"  
        "&pageType=all"  
        "&indexCode=uv")
    payload = {}
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
    }

    response = session.request("GET", url, headers=headers, data=payload)
    response_json = response.json()

    # 提取UV（用户指定）
    uv = response_json["data"]["data"][0]["uv"]["value"]
    logging.info(f"uv的值为{uv}")
    return uv
