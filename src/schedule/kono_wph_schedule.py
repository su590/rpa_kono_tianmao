
import dataclasses
import datetime
import json
import logging
import os

from src.schedule import PATH
from src.spider.wph.WphGysLogin import WphGysSession
from src.spider.wph.commodity_rank import get_commodity_data, _CommodityRank
from src.utils.feishutools import insert_spread_append

# sheets
SPREAD_SHEET_TOKEN = 'ATcfsn7aJhOn7dtFHTlcTrjonug'
# sheet 人气榜单
SHEET_TOKEN_POPULAR = 'T0KKFs'
# sheet 销售榜单
SHEET_TOKEN_SALE = '0jiSmW'

# 唯品会登录的账密实体类
@dataclasses.dataclass
class _WphAccount:
    username: str
    password: str
    port: int

def _get_wph_account() -> _WphAccount:
    """
    从json文件当中读取出唯品会的账密信息
    :return:
    """
    path = os.path.join(PATH, 'wph_account.json')
    with open(path, 'r', encoding='utf-8') as f:
        account_dict: dict = json.load(f)[0]
        return _WphAccount(**account_dict)

def _upload(_commodity_rank_list: list[_CommodityRank], sheet_token: str, date_str: str) -> None:
    """
    把榜单数据上传到飞书云表格上面
    :param _commodity_rank_list: 榜单数据列表
    :param sheet_token: 飞书 sheet_id
    """
    if not _commodity_rank_list:
        logging.warning("榜单数据为空，跳过上传")
        return

    # 转换成二维数组
    values = []
    for item in _commodity_rank_list:
        values.append([
            date_str,                      # 日期
            item.rank,                          # 排名
            item.commodityInfo.merchandiseNo,   # 商品编号
            item.commodityInfo.goodsName,       # 商品名称
            item.commodityInfo.prodSpuId,       # prodSpuId
            item.imgUrl,                        # 图片地址
            item.brandStoreName,                # 品牌店铺
            item.minPayPrice,                   # 最低支付价格
            item.pageMerDetailFlowIndex,        # 详情页流量指数
            item.ctrIndex,                      # 点击率指数
            item.addUserNumIndex,               # 加购人数指数
            item.goodsActureAmtIndex,           # 成交金额指数
            item.goodsActureNumIndex,           # 成交件数指数
            item.convRateIndex,                 # 转化率指数
            item.unitPriceIndex                 # 客单价指数
        ])

    # 批量追加
    insert_spread_append(SPREAD_SHEET_TOKEN, sheet_token, values)


def get_and_upload_rank_data() -> None:
    """
    获取唯品会的排名信息 并且将其上传到飞书在线表格上面
    :return:
    """
    _wph_account = _get_wph_account()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    with WphGysSession(_wph_account.username, _wph_account.password, _wph_account.port) as session:
        # 传入参数为1、2分别代表人气榜单和销售榜单
        popular_rank_list = get_commodity_data(session, 1, yesterday)
        sale_rank_list = get_commodity_data(session, 2, yesterday)
        # 分别将两个榜单的数据上传
        _upload(popular_rank_list, SHEET_TOKEN_POPULAR, yesterday.strftime('%Y%m%d'))
        _upload(sale_rank_list, SHEET_TOKEN_SALE, yesterday.strftime('%Y%m%d'))

if __name__ == '__main__':
    get_and_upload_rank_data()