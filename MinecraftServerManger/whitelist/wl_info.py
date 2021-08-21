#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import traceback

from graia.application.entry import (GraiaMiraiApplication, MessageChain, Plain, At, Source, Group)
import requests
import urllib3

from ..api import get_mc_id, get_uuid, is_mc_id
from ..info import MODULE_NAME
from .config import read_cfg
from .db import execute_query_sql

from graia.application.exceptions import UnknownTarget

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')
cfg = read_cfg()


async def query_wl_by_qq(qq: int, app: GraiaMiraiApplication, group: Group, message: MessageChain):
    query_sql = f'select main_uuid,main_add_time,alt_uuid,alt_add_time from {cfg["table"]} where qq={qq};'
    try:
        res = execute_query_sql(query_sql)
    except Exception as e:  # noqa
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'在数据库查询QQ【{qq}】拥有的白名单时出错: ↓\n{str(e)}')
        ]), quote=message.get(Source).pop(0))
        logger.error(f'在数据库查询QQ【{qq}】拥有的白名单时出错: ↓\n{traceback.format_exc()}')
        return
    if res is None:
        try:
            await app.sendGroupMessage(group, MessageChain.create([
                At(qq),
                Plain(f'({qq}) 好像一个白名单都没有呢~')
            ]))
        except UnknownTarget:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'{qq} 好像一个白名单都没有呢~')
            ]))
        finally:
            return
    try:
        get_id1_res = get_mc_id(res[0])
        # 本来会返回 None-不是uuid 或 http code 204-找不到该uuid的玩家 或 http code 400-uuid格式错误
        # 这里因为时从数据库读取的uuid，所以忽略这几种情况
    except (requests.exceptions.Timeout, urllib3.exceptions.TimeoutError):
        msg_send = f'| 大号ID: {res[0]}'
    else:
        msg_send = f'| 大号ID: {get_id1_res}'
    msg_send += f'\n|  > 添加时间: {res[1]}'
    if res[3] is not None:
        try:
            get_id2_res = get_mc_id(res[2])
            # 本来会返回 None-不是uuid 或 http code 204-找不到该uuid的玩家 或 http code 400-uuid格式错误
            # 这里因为时从数据库读取的uuid，所以忽略这几种情况
        except (requests.exceptions.Timeout, urllib3.exceptions.TimeoutError):
            msg_send += f'| 小号ID: {res[2]}'
        else:
            msg_send += f'| 小号ID: {get_id2_res}'
        msg_send += f'\n|  > 添加时间: {res[3]}'
    try:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('QQ: '), At(qq), Plain(f' ({res[0]})\n'), Plain(msg_send)
        ]))
    except UnknownTarget:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'QQ: {qq}\n{msg_send}')
        ]))


async def query_wl_by_id(mc_id: str, app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if not is_mc_id(mc_id):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('你选择的不是一个有效的id')
        ]))
        return
    try:
        mc_id, uuid = get_uuid(mc_id)
    except (requests.exceptions.Timeout, urllib3.exceptions.TimeoutError):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'向 mojang 查询【{mc_id}】的 uuid 超时')
        ]))
        return
    except Exception as e:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'向 mojang 查询【{mc_id}】的 uuid 时发生了意料之外的错误:  ↓\n{str(e)}')
        ]))
        logger.error(f'向 mojang 查询【{mc_id}】的 uuid 时发生了意料之外的错误:  ↓\n{traceback.format_exc()}')
        return
    if uuid is None:
        code = mc_id
        if code == 204:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('你选择的不是一个正版id')
            ]))
            return
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'向 mojang 查询【{mc_id}】的 uuid 时，服务器阿巴阿巴了')
            ]))
            return
    query_sql = f'select qq from {cfg["table"]} where main_uuid=\'{uuid}\' OR alt_uuid=\'{uuid}\';'
    try:
        res = execute_query_sql(query_sql)
    except Exception as e:  # noqa
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'在数据库查询 uuid【{uuid}】对应的qq时出错: ↓\n{str(e)}')
        ]), quote=message.get(Source).pop(0))
        logger.error(f'在数据库查询 uuid【{uuid}】对应的qq时出错: ↓\n{traceback.format_exc()}')
        return
    if res is None:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'好像没有使用{mc_id}的玩家呢~')
        ]))
        return
    await query_wl_by_qq(res[0], app, group, message)


async def whitelist_info(*args, message: MessageChain, **kwargs):
    if len(args) == 3:
        if message.has(At):
            await query_wl_by_qq(qq=message.get(At)[0].dict()['target'], message=message, **kwargs)
            return 0
    elif len(args) == 4:
        if args[2].lower() == 'qq':
            if message.has(At):
                await query_wl_by_qq(qq=message.get(At)[0].dict()['target'], message=message, **kwargs)
                return 0
            elif args[3].isdigit():
                await query_wl_by_qq(qq=int(args[3]), **kwargs)
                return 0
        elif args[2].lower() == 'id':
            await query_wl_by_id(args[3], message=message, **kwargs)
            return 0