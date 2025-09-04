# -*- coding: utf-8 -*-  
"""
@Date     : 2025-02-21
@Author   : xwq
@Desc     : <None>

"""
import logging
import typing

import pymysql
from dbutils.pooled_db import PooledDB, PooledDedicatedDBConnection
from dbutils.steady_db import SteadyDBCursor

from src.config import get_config


def _pool() -> PooledDB:
    return PooledDB(
        creator=pymysql,
        mincached=get_config('mysql', 'mincached'),
        maxcached=get_config('mysql', 'maxcached'),
        maxshared=get_config('mysql', 'maxshared'),
        maxconnections=get_config('mysql', 'maxconnections'),
        blocking=True,
        maxusage=get_config('mysql', 'maxusage'),
        host=get_config('mysql', 'host'),
        port=get_config('mysql', 'port'),
        user=get_config('mysql', 'user'),
        passwd=get_config('mysql', 'password'),
        db=get_config('mysql', 'database'),
    )


_LOGGER = logging.getLogger('sqltools')
_POOL = _pool()


def _connect() -> tuple[PooledDedicatedDBConnection, SteadyDBCursor]:
    conn = _POOL.connection()
    cur = conn.cursor()
    return conn, cur


def _disconnect(conn, cur) -> None:
    cur.close()
    conn.close()


class SqlHelper:
    """
    用于快捷使用连接池，如：
    with SqlHelper() as sh:
        sh.execute('select * from table')
    """

    def __init__(self, both: bool = False):
        self.both = both

    def __enter__(self) -> SteadyDBCursor | tuple[PooledDedicatedDBConnection, SteadyDBCursor]:
        self.__conn, self.__cur = _connect()
        if self.both:
            return self.__conn, self.__cur
        else:
            return self.__cur

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        _disconnect(self.__conn, self.__cur)


def select(sql: str, data: typing.Sequence) -> dict[str, typing.Any]:
    """
    通用的数据库查询
    :param sql: sql语句
    :param data: 参数序列，如[1, "name"]
    :return: {字段名: 字段值}
    """
    _LOGGER.debug(f'sql=\n{sql}\ndata={data}')
    with SqlHelper() as cursor:
        cursor.execute(sql, data)
        result = cursor.fetchone()
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, result))


def selectall(sql: str, data: typing.Sequence) -> list[dict[str, typing.Any]]:
    """
    通用的数据库查询
    :param sql: sql语句
    :param data: 参数序列，如[1, "name"]
    :return: [{字段名: 字段值}]
    """
    _LOGGER.debug(f'sql=\n{sql}\ndata={data}')
    with SqlHelper() as cursor:
        cursor.execute(sql, data)
        results = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, result)) for result in results]


def update(sql: str, data: typing.Sequence) -> int:
    """
    通用的数据库更新
    :param sql: sql语句
    :param data: 参数序列，如[1, "name"]
    :return: 影响行数
    """
    _LOGGER.debug(f'sql=\n{sql}\ndata={data}')
    with SqlHelper(True) as (conn, cur):
        try:
            result = cur.execute(sql, data)
            conn.commit()
            return result
        except Exception as e:
            # _LOGGER.error(f'执行sql出错: {e}')
            # _LOGGER.error(f'traceback: {traceback.format_exc()}')
            # conn.rollback()
            # return 0
            conn.rollback()
            raise e


def updateall(sql: str, data: typing.Sequence) -> int:
    """
    通用的数据库更新
    :param sql: sql语句
    :param data: 参数序列，如[1, "name"]
    :return: 影响行数
    """
    _LOGGER.debug(f'sql=\n{sql}\ndata={data}')
    with SqlHelper(True) as (conn, cur):
        try:
            result = cur.executemany(sql, data)
            conn.commit()
            return result
        except Exception as e:
            # _LOGGER.error(f'执行sql出错: {e}')
            # _LOGGER.error(f'traceback: {traceback.format_exc()}')
            # conn.rollback()
            # return 0
            conn.rollback()
            raise e
