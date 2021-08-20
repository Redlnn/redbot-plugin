#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sqlite3
import traceback
import os
from typing import Union
from pymysql.cursors import Cursor

import pymysql

from ..info import MODULE_NAME
from .config import read_cfg


logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')
cfg = read_cfg()


def _connect_db() -> Union[pymysql.Connection, sqlite3.Connection]:
    database_name = cfg['database']
    if cfg['mysql']['enable']:
        host = cfg['mysql']['host']
        user = cfg['mysql']['user']
        password = cfg['mysql']['password']
        port = cfg['mysql']['port']
        try:
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                port=port,
                database=database_name,
                charset='utf8')
        except:  # noqa
            logger.error(f'白名单MySQL数据库连接失败: ↓\n{traceback.format_exc()}')
            raise ValueError('白名单MySQL数据库连接失败')
    else:
        database_folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
        if not os.path.exists(database_folder_path):
            os.mkdir(database_folder_path)
        elif os.path.isfile(database_folder_path):
            os.remove(database_folder_path)
            os.mkdir(database_folder_path)
        try:
            conn = sqlite3.connect(os.path.join(database_folder_path, 'whitelist.db'))
        except:  # noqa
            logger.error(f'无法打开白名单SQLite数据库: ↓\n{traceback.format_exc()}')
            raise ValueError('无法打开白名单SQLite数据库')
    return conn


def _init_db() -> tuple[Union[pymysql.Connection, sqlite3.Connection], Union[sqlite3.Cursor, Cursor]]:
    conn = _connect_db()
    cur = conn.cursor()
    if cfg['mysql']['enable']:
        conn.ping(reconnect=True)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS `{cfg['table']}` (" \
                           "`qq` bigint(12) PRIMARY KEY not null comment '绑定的QQ号'," \
                           "`main_uuid` varchar(37) default null comment '该QQ绑定的mc大号的uuid'," \
                           "`main_add_time` datetime default null comment '该QQ绑定mc大号的时间'," \
                           "`alt_uuid` varchar(37) default null comment '该QQ绑定的mc小号的uuid'," \
                           "`alt_add_time` datetime default null comment '该QQ绑定mc小号的时间'" \
                           ") DEFAULT CHARSET 'utf8mb4';"
    else:
        create_table_sql = f"CREATE TABLE IF NOT EXISTS `{cfg['table']}` (" \
                           "`qq` bigint(12) PRIMARY KEY not null," \
                           "`main_uuid` varchar(37) default null," \
                           "`main_add_time` datetime default null," \
                           "`alt_uuid` varchar(37) default null," \
                           "`alt_add_time` datetime default null);"
    cur.execute(create_table_sql)
    return conn, cur


def execute_query_sql(sql_command: str):
    conn, cur = _init_db()
    try:
        cur.execute(sql_command)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def execute_update_sql(sql_command: str):
    conn, cur = _init_db()
    try:
        cur.execute(sql_command)
    finally:
        cur.close()
        conn.commit()
        conn.close()


__all__ = [execute_query_sql, execute_update_sql]
