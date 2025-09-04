# -*- coding: utf-8 -*-  
"""
@Date     : 2025-02-20
@Author   : xwq
@Desc     : <None>

"""
import dataclasses
import datetime
import json
import logging
import time
from typing import Callable

import requests


@dataclasses.dataclass
class Sms:
    date: datetime.datetime
    message: str


def _default(v, default):
    if v is None:
        return default
    return v


def get_sms(
        phone: str,
        date: datetime.datetime = None,
        limit: int = None,
        match: str = None,
) -> list[Sms]:
    """
    获取最新的短信
    参考 https://jqx28l0j4lx.feishu.cn/wiki/SN5hwjtkdif6tUknbu1c6wp3n4g
    :param phone: 目标手机
    :param date: 开始时间点
    :param limit: 最大短信数量
    :param match: 模糊匹配
    """
    date = _default(date, datetime.datetime.now() - datetime.timedelta(minutes=5))
    limit = _default(limit, 100)
    match = _default(match, '')
    for _ in range(3):
        # 请求
        url = "http://cloud.fandow.com/prcp/mdm/receive/rpa/sms"
        payload = json.dumps({
            "phone": phone,
            "date": date.strftime('%Y-%m-%d %H:%M:%S'),
            "limit": limit,
            "match": match
        })
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        jsn = response.json()

        # 转化
        if jsn['code'] != 0:
            logging.error(f'服务器异常, 请求短信失败, {jsn=}')
            continue

        return [Sms(**x) for x in jsn.get('data', [])]
    raise ValueError('服务器异常, 请求短信失败')


def wait_sms(
        phone: str,
        date: datetime.datetime = None,
        limit: int = None,
        match: str = None,
        timeout: int = 60 * 10,
) -> list[Sms]:
    """
    等待最新的短信
    参考 https://jqx28l0j4lx.feishu.cn/wiki/SN5hwjtkdif6tUknbu1c6wp3n4g
    :param phone: 目标手机
    :param date: 开始时间点
    :param limit: 最大短信数量
    :param match: 模糊匹配
    :param timeout: 限时, 在规定时间内取值应不为空
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        result = get_sms(phone, date, limit, match)
        if len(result) > 0:
            return result
        time.sleep(1)
    result = get_sms(phone, date, limit, match)
    if len(result) > 0:
        return result
    raise TimeoutError(f'在规定时间({timeout}s)内未能成功取得符合条件的短信')


def get_codes(
        phone: str,
        msg2code: Callable[[str], str | None],
        date: datetime.datetime = None,
        limit: int = None,
) -> list[str]:
    """
    获取最新的短信验证码
    参考 https://jqx28l0j4lx.feishu.cn/wiki/SN5hwjtkdif6tUknbu1c6wp3n4g
    :param phone: 目标手机
    :param msg2code: 入参为短信内容, 出餐为验证码的方法
    :param date: 开始时间点
    :param limit: 最大短信数量
    """
    smss = get_sms(phone, date, limit, '')
    codes = []
    for sms in smss:
        code = msg2code(sms.message)
        if code is not None:
            codes.append(code)
    return codes


def wait_codes(
        phone: str,
        msg2code: Callable[[str], str | None],
        date: datetime.datetime = None,
        limit: int = None,
        timeout: int = None,
) -> list[str]:
    """
    等待最新的短信验证码
    参考 https://jqx28l0j4lx.feishu.cn/wiki/SN5hwjtkdif6tUknbu1c6wp3n4g
    :param phone: 目标手机
    :param msg2code: 入参为短信内容, 出餐为验证码的方法
    :param date: 开始时间点
    :param limit: 最大短信数量
    :param timeout: 限时, 在规定时间内取值应不为空
    """
    timeout = _default(timeout, 60 * 10)
    start_time = time.time()
    while time.time() - start_time <= timeout:
        codes = get_codes(phone, msg2code, date, limit)
        if len(codes) > 0:
            return codes
        time.sleep(1)
    codes = get_codes(phone, msg2code, date, limit)
    if len(codes) > 0:
        return codes
    raise TimeoutError(f'在规定时间({timeout}s)内未能成功取得符合条件的短信')
