# -*- coding: utf-8 -*-  
"""
@Date     : 2025-03-25
@Author   : xwq
@Desc     : <None>

"""
import decimal
from functools import singledispatch
from typing import Any, Iterable


@singledispatch
def integer(v) -> int:
    raise ValueError(f'暂未适配值为"{v}", 类型为{type(v)}的int转化')


@integer.register(int)
def _(v: int):
    return v


@integer.register(str)
def _(v: str):
    v = v.replace(',', '')
    v = v.replace(' ', '')
    if v.endswith('万'):
        v = float(v[:-1]) * 10000
    elif v.endswith('w'):
        v = float(v[:-1]) * 10000
    elif v.endswith('亿'):
        v = float(v[:-1]) * (10 ** 8)
    elif v.endswith('千'):
        v = float(v[:-1]) * 1000
    return int(v)


@singledispatch
def dcml(v) -> decimal.Decimal | None:
    if v is None:
        return None
    raise ValueError(f'暂未适配值为"{v}", 类型为{type(v)}的decimal转化')


@dcml.register(decimal.Decimal)
def _(v: decimal.Decimal):
    return v


@dcml.register(int)
def _(v: int):
    return decimal.Decimal(v)


@dcml.register(float)
def _(v: float):
    return decimal.Decimal(v)


@dcml.register(str)
def _(v: str):
    v = v.replace(',', '')
    v = v.replace(' ', '')
    if v in ('-', ''):
        return None
    if v[-1] == '万':
        return decimal.Decimal(v[:-1]) * decimal.Decimal(10000)
    if v[-1] == '亿':
        return decimal.Decimal(v[:-1]) * decimal.Decimal(10 ** 8)
    if v[-1] == 'w':
        return decimal.Decimal(v[:-1]) * decimal.Decimal(10000)
    elif v[-1] == '%':
        return decimal.Decimal(v[:-1]) / decimal.Decimal(100)
    return decimal.Decimal(v)


def default(v, df=None) -> Any:
    """
    设置默认值
    :param v:
    :param df:
    :return:
    """
    if v is None:
        return df
    else:
        return v


def combination(*sequences: Iterable):
    if len(sequences) == 0:
        return None
    if len(sequences) == 1:
        for x in sequences[0]:
            yield (x,)
        return
    for x in sequences[0]:
        for y in combination(*sequences[1:]):
            yield x, *y
