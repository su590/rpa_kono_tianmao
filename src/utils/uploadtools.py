# -*- coding: utf-8 -*-  
"""
@Date     : 2025-03-13
@Author   : xwq
@Desc     : <None>

参考 https://jqx28l0j4lx.feishu.cn/wiki/M1ypwHAeiiZOyfkCWWWcysUBnnh

"""
import dataclasses
import datetime
import json

import requests

from src import get_config


@dataclasses.dataclass
class Note:
    note_id: str
    plat: str
    title: str
    pics: list[str]
    videos: list[str]
    publish_date: datetime.date | None
    publish_addr: str | None
    publisher: str
    content: str
    link: str | None
    keyword: str
    tag: str
    rank: int


_passport = get_config('upload', 'passport')


def upload_note(note: Note) -> dict:
    """
    回传笔记
    :param note:
    :return:
    """
    url = get_config('upload', 'rpa_note')
    payload = dataclasses.asdict(note)
    if note.publish_date is not None:
        payload['publish_date'] = note.publish_date.strftime('%Y-%m-%d')
    payload = json.dumps(payload, ensure_ascii=False)
    headers = {
        'Content-Type': 'application/json',
        'passport': _passport
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


@dataclasses.dataclass
class Comment:
    plat: str
    comment_id: str
    content: str
    note_id: str
    comment_time: datetime.datetime
    commenter: str
    comment_addr: str | None


def upload_comment(comment: Comment) -> dict:
    """
    回传评论
    :param comment:
    :return:
    """
    url = get_config('upload', 'rpa_comment')
    payload = dataclasses.asdict(comment)
    if comment.comment_time is not None:
        payload['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
    payload = json.dumps(payload, ensure_ascii=False)
    headers = {
        'Content-Type': 'application/json',
        'passport': _passport
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


@dataclasses.dataclass
class NoteRecord:
    note_id: str
    plat: str
    keyword: str
    tag: str
    rank: int


def upload_note_record(record: NoteRecord) -> dict:
    """
    回传笔记记录
    :param record:
    :return:
    """
    url = get_config('upload', 'rpa_note_record')
    payload = dataclasses.asdict(record)
    payload = json.dumps(payload, ensure_ascii=False)
    headers = {
        'Content-Type': 'application/json',
        'passport': _passport
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


@dataclasses.dataclass
class Keyword:
    id: int
    keyword: str


def get_keywords() -> list[Keyword]:
    """
    取关键词
    :return:
    """
    url = get_config('upload', 'rpa_keywords')
    headers = {'Content-Type': 'application/json', 'passport': _passport}
    response = requests.request("GET", url, headers=headers)
    jsn = response.json()
    result = [Keyword(**x) for x in jsn['data']['keywords']]
    return result


@dataclasses.dataclass
class ExistParam:
    plat: str
    note_id: str


def exist_note_id(param: ExistParam) -> bool:
    """
    是否存在该note_id
    :param param:
    :return:
    """
    url = get_config('upload', 'rpa_nid_exist')
    payload = dataclasses.asdict(param)
    payload = json.dumps(payload, ensure_ascii=False)
    headers = {'Content-Type': 'application/json', 'passport': _passport}
    response = requests.request("POST", url, headers=headers, data=payload)
    jsn = response.json()
    return jsn['data']['exist']


def oss_exist(oss_key: str) -> bool:
    """
    是否存在该key
    :param oss_key:
    :return:
    """
    url = get_config('upload', 'rpa_oss_exist')
    url = f'{url}/{oss_key}'
    headers = {'Content-Type': 'application/json', 'passport': _passport}
    response = requests.request("GET", url, headers=headers)
    jsn = response.json()
    return jsn['data']['exist']


def oss_add(oss_key: str) -> int:
    """
    新增key
    :param oss_key:
    :return:
    """
    url = get_config('upload', 'rpa_oss_add')
    url = f'{url}/{oss_key}'
    headers = {'Content-Type': 'application/json', 'passport': _passport}
    response = requests.request("GET", url, headers=headers)
    jsn = response.json()
    return jsn['data']['effect']


def report_comment_count(plat: str, note_id: str, count: str) -> bool:
    """
    上报评论数，并反馈是否发生改变
    :param plat:
    :param note_id:
    :param count:
    :return:
    """
    url = get_config('upload', 'rpa_comment_count')
    headers = {'Content-Type': 'application/json', 'passport': _passport}
    payload = {'plat': plat, 'note_id': note_id, 'count': count}
    payload = json.dumps(payload, ensure_ascii=False)
    response = requests.request("POST", url, headers=headers, data=payload)
    jsn = response.json()
    return jsn['data']['change']


def report_comment_fail(plat: str, note_id: str) -> int:
    """
    上报评论抓取失败
    :param plat:
    :param note_id:
    :return:
    """
    url = get_config('upload', 'rpa_comment_fail')
    url = f'{url}/{plat}/{note_id}'
    headers = {'Content-Type': 'application/json', 'passport': _passport}
    response = requests.request("GET", url, headers=headers)
    jsn = response.json()
    return jsn['data']['effect']
