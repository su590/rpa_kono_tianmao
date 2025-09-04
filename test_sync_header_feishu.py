from src.utils.feishutools import insert_spread_append

if __name__ == '__main__':
    headers = [
        "日期", "排名", "商品编号", "商品名称", "prodSpuId", "图片地址", "品牌店铺",
        "最低支付价格", "详情页流量指数", "点击率指数", "加购人数指数", "成交金额指数",
        "成交件数指数", "转化率指数", "客单价指数"
    ]
    insert_spread_append('ATcfsn7aJhOn7dtFHTlcTrjonug', '0jiSmW', headers)
    insert_spread_append('ATcfsn7aJhOn7dtFHTlcTrjonug', 'T0KKFs', headers)
