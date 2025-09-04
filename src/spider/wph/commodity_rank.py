import dataclasses
import json
from datetime import datetime
from requests import Session

@dataclasses.dataclass
class _CommodityInfo:
    merchandiseNo: str #MID
    goodsName: str
    prodSpuId: str #PSPUID

# 获取唯品会的商品排名
@dataclasses.dataclass
class _CommodityRank:
    rank: int
    imgUrl: str
    commodityInfo: _CommodityInfo
    brandStoreName: str
    minPayPrice: float
    pageMerDetailFlowIndex: int
    ctrIndex: int
    addUserNumIndex: int
    goodsActureAmtIndex: int
    goodsActureNumIndex: int
    convRateIndex: int
    unitPriceIndex: int

def _get_rank(session: Session, order_field: int, date_time: datetime) -> list:
    """
    在唯品会 - 魔方罗盘
    :param session:
    :param order_field: 人气榜单：1 销售榜单：2
    :return:
    """
    date_str: str = date_time.strftime('%Y%m%d')

    url = "https://compass.vip.com/industry/industrySituation/queryIndustryMerRanking"
    payload = json.dumps({
        "startDt": date_str,
        "endDt": date_str,
        "dtType": 0,
        "brandStoreSn": "10040918",
        "categoryLevel": 1,
        "categoryId": 7470,
        "orderField": order_field
    })
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://compass.vip.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://compass.vip.com/frontend/index.html',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
    }

    response = session.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    return response_json['data']['rankingDataList']

def _assemble_data(rank_list: list) -> list:
    """
    返回组装的前100名数据 并保存在表格当中
    :param rank_list: 原始商品字典列表
    :return:
    """
    data_objects = []
    for item in rank_list[:100]:
        # 构造商品信息对象
        info = _CommodityInfo(merchandiseNo=item['merchandiseNo'], goodsName=item['goodsName'], prodSpuId=item['prodSpuId'])
        # 构造商品排名对象
        rank_obj = _CommodityRank(
            rank=item['ranking'],
            imgUrl=item['imgUrl'],
            commodityInfo=info,
            brandStoreName=item['brandStoreName'],
            minPayPrice=item['minPayPrice'],
            pageMerDetailFlowIndex=item['pageMerDetailFlowIndex'],
            ctrIndex=item['ctrIndex'],
            addUserNumIndex=item['addUserNumIndex'],
            goodsActureAmtIndex=item['goodsActureAmtIndex'],
            goodsActureNumIndex=item['goodsActureNumIndex'],
            convRateIndex=item['convRateIndex'],
            unitPriceIndex=item['unitPriceIndex']
        )

        data_objects.append(rank_obj)
    return data_objects

def get_commodity_data(session: Session, order_field: int, date_time: datetime) -> list[_CommodityRank]:
    """
    拿到当前日期的商品排名
    :param session:
    :param order_field: 1: 人气榜单 2: 销售榜单
    :param date_time: 时间
    :return: list[_CommodityRank]
    """
    return _assemble_data(_get_rank(session, order_field, date_time))