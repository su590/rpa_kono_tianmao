"""
对接飞书用到的相关工具
"""
import datetime
import json
import logging

import requests

def send_message_by_robot(content: str, robot_url: str) -> dict:
    """
       Args:
           content: 发送的内容
           robot_url: 机器人链接

       Returns:

       """
    headers = {"Content-Type": "application/json; charset=utf-8"}
    msg = {
        "msg_type": "text",
        "content": {"text": content}
    }
    rep = requests.request(
        method="post", headers=headers,
        url=robot_url, data=json.dumps(msg)
    )
    return rep.json()

def _get_column_letter(num: int) -> str:
    """
    :param num: 一共有多少列
    :return: 最后一列的列名 在表格当中最后一列的列名
    """
    letters = ""
    while num > 0:
        num -= 1
        letters = chr(num % 26 + 65) + letters
        num //= 26
        print(f'last column: {letters}')
    return letters

def _get_tenant_access_token() -> str:
    """
    获取租户的token
    Returns:

    """
    ans = requests.post(url='https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
                        data={
                            "app_id": "cli_a441b931043b9013",
                            "app_secret": "5i78C0KAeSJuLDSzloEECdSCYRfrCST2"
                        }
                        )
    return ans.json()["tenant_access_token"]


def insert_spread_cover(spreadsheet_token: str, sheet_id: str, insert_list: list, row_start: int):
    """
    向飞书表格的指定行写入一行数据（覆盖写入）

    Args:
        spreadsheet_token: 表格 token
        sheet_id: 表格 sheet ID
        insert_list: 单行数据（list）
        row_start: 起始行号
    """
    if not insert_list:
        logging.warning("插入数据为空，跳过写入")
        return

    num_cols = len(insert_list)
    last_column_alpha = _get_column_letter(num_cols)
    range_str = f'{sheet_id}!A{row_start}:{last_column_alpha}{row_start}'

    url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values'
    data = {
        "valueRange": {
            "range": range_str,
            "values": [insert_list]  # 一行数据包装成二维数组
        }
    }

    headers = {
        'Authorization': 'Bearer ' + _get_tenant_access_token(),
        'Content-Type': 'application/json'
    }

    ans = requests.put(url=url, data=json.dumps(data), headers=headers).json()
    if ans["code"] == 0:
        logging.info(f"成功写入数据到第 {row_start} 行：{insert_list}")
    else:
        logging.warning("写入数据失败，错误信息：%s", ans)

def insert_spread_append(spreadsheet_token: str, sheet_id: str, insert_list: list):
    """
    向飞书表格末尾追加数据，自动判断是单行还是多行
    """
    if not insert_list:
        logging.warning("插入数据为空，跳过插入")
        return

    # 判断是否是批量数据
    if isinstance(insert_list[0], list):
        values = insert_list
    else:
        values = [insert_list]

    url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_append'
    data = {
        "valueRange": {
            "range": sheet_id,
            "values": values
        }
    }

    headers = {
        'Authorization': 'Bearer ' + _get_tenant_access_token(),
        'Content-Type': 'application/json'
    }

    ans = requests.post(url=url, data=json.dumps(data), headers=headers).json()
    if ans["code"] == 0:
        logging.info("在表格中成功追加数据")
    else:
        logging.warning("追加数据失败，错误信息：%s", ans)

def insert_spread_part(insert_info: list, spreadsheet_token: str, sheet_id: str, range: str):
    """
    在表格中按照范围添加信息
    Args:
        insert_info: 添加的信息列表
        spreadsheet_token: 从电子表格的url当中获取
        sheet_id: 工作表id 要从飞书开发者平台上面拿
        range: 列返回 示例：A：C

    Returns:

    """
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_append"
    headers = {
        'Authorization': 'Bearer ' + _get_tenant_access_token(),
        'Content-Type': 'application/json'
    }
    data = {
        "valueRange": {
            "range": f"{sheet_id}!{range}",
            "values": [
                insert_info
            ]
        }
    }
    ans = requests.request("POST", url, headers=headers, data=json.dumps(data)).json()
    if ans["code"] == 0:
        logging.info(f"在表格{range}中添加数据成功")
    else:
        logging.warning(f"在表格{range}中添加数据失败")

def get_time_period_per_30min() -> str:
    """
    获取到时间信息格式为：{hour}:{minute_start}-{hour}:{minute_end}

    Returns:

    """
    time_obj = datetime.datetime.strptime(
        datetime.datetime.now().strftime("%H:%M:%S"),
        "%H:%M:%S")
    minute = time_obj.minute
    if minute >= 30:
        hour = time_obj.hour  # 当前小时
        minute_start = '00'
        minute_end = '30'  # 上个30min
    else:
        hour = time_obj.hour - 1 if time_obj.hour != 0 else 23  # 上个小时
        minute_start = '30'
        minute_end = '59'

    time_period = f"{hour}:{minute_start}-{hour}:{minute_end}"
    return time_period

def get_time_period_per_hour() -> str:
    """
    获取到时间信息格式为：{hour_prev}:00-{hour}:00

    Returns:
        str: 上一个小时到当前小时的时间段，例如 "9:00-10:00"
    """
    # 获取当前时间
    time_obj = datetime.datetime.strptime(
        datetime.datetime.now().strftime("%H:%M:%S"),
        "%H:%M:%S"
    )
    hour = time_obj.hour  # 当前小时
    hour_prev = hour - 1 if hour != 0 else 23  # 上一个小时

    # 构造时间段
    time_period = f"{hour_prev}:00-{hour}:00"
    return time_period

if __name__ == '__main__':
    pass