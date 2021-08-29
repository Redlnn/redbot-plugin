#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import traceback
from typing import Union

import requests
import urllib3
from graia.application.entry import (GraiaMiraiApplication, MessageChain, Plain, At, Source, Group)

from .config import read_cfg
from .db import execute_query_sql, execute_update_sql
from .utils import check_qq_had_id
from ..api import get_uuid, is_mc_id, get_time, PermissionCheck, LengthCheck
from ..info import MODULE_NAME
from ..rcon.rcon import execute_command

__all__ = [
    "add_whitelist", "add_whitelist_to_qq"
]

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')
cfg = read_cfg()


async def _check_id_in_use(
        uuid: str, app: GraiaMiraiApplication, message: MessageChain, group: Group) -> Union[bool, int, None]:
    query_sql = f'select qq from {cfg["table"]} where main_uuid=\"{uuid}\" or alt_uuid=\"{uuid}\";'
    try:
        res = execute_query_sql(query_sql)
    except Exception as e:  # noqa
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'在数据库查询【{uuid}】是否被占用时出错: ↓\n{str(e)}')
        ]), quote=message.get(Source).pop(0))  # noqa
        logger.error(f'在数据库查询【{uuid}】是否被占用时出错: ↓\n{traceback.format_exc()}')
        return False

    if res:  # 被占用
        return int(res[0])
    else:  # 没被占用
        return None


async def add_whitelist_to_qq(
        qq: int, mc_id: str, app: GraiaMiraiApplication, message: MessageChain, group: Group, **kwagrs):
    if not is_mc_id(mc_id):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('你选择的不是一个有效的id')
        ]), quote=message.get(Source).pop(0))  # noqa

    try:
        real_mc_id, uuid = get_uuid(mc_id)
    except (requests.exceptions.Timeout, urllib3.exceptions.TimeoutError):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'向 mojang 查询【{mc_id}】的 uuid 超时')
        ]), quote=message.get(Source).pop(0))  # noqa
        return
    except Exception as e:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'向 mojang 查询【{mc_id}】的 uuid 时发生了意料之外的错误:  ↓\n{str(e)}')
        ]), quote=message.get(Source).pop(0))  # noqa
        logger.error(f'向 mojang 查询【{mc_id}】的 uuid 时发生了意料之外的错误:  ↓\n{traceback.format_exc()}')
        return

    use_status = await _check_id_in_use(uuid, app, message, group)
    if use_status is False:
        return
    elif type(use_status) == int:
        if use_status == qq:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('这个id本来就是你哒')
            ]), quote=message.get(Source).pop(0))  # noqa
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('你想要这个吗？\n这个是 '),
                At(use_status),
                Plain(f'({use_status}) 哒~'),
            ]), quote=message.get(Source).pop(0))  # noqa
        return

    had_status = await check_qq_had_id(qq, app, message, group)
    if had_status[0] == 'error':  # 检查该QQ是否已经申请白名单
        return  # 出错了
    elif had_status[0] == 'null':  # main和alt位均为空
        insert_sql = f'insert into {cfg["table"]} (qq, main_uuid, main_add_time) ' \
                     f'values ({qq}, \'{uuid}\', \'{get_time()}\');'
        try:
            execute_update_sql(insert_sql)
        except Exception as e:  # noqa
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'在数据库写入QQ【{qq}】的白名单时出错: ↓\n{str(e)}')
            ]), quote=message.get(Source).pop(0))  # noqa
            logger.error(f'在数据库写入QQ【{qq}】的白名单时出错: ↓\n{traceback.format_exc()}')
            return
    elif had_status[1] == 1:  # alt位为空
        update_uuid_sql = f'update {cfg["table"]} set alt_uuid=\'{uuid}\' where qq={qq};'
        update_time_sql = f'update {cfg["table"]} set alt_add_time=\'{get_time()}\' where qq={qq};'
        try:
            execute_update_sql(update_uuid_sql)
            execute_update_sql(update_time_sql)
        except Exception as e:  # noqa
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'在数据库写入QQ【{qq}】的第二个白名单时出错: ↓\n{str(e)}')
            ]), quote=message.get(Source).pop(0))  # noqa
            logger.error(f'在数据库写入QQ【{qq}】的第二个白名单时出错: ↓\n{traceback.format_exc()}')
            return
    elif had_status[1] == 2:  # main位为空
        update_uuid_sql = f'update {cfg["table"]} set main_uuid=\'{uuid}\' where qq={qq};'
        update_time_sql = f'update {cfg["table"]} set main_add_time=\'{get_time()}\' where qq={qq};'
        try:
            execute_update_sql(update_uuid_sql)
            execute_update_sql(update_time_sql)
        except Exception as e:  # noqa
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'在数据库写入QQ【{qq}】的第二个白名单时出错: ↓\n{str(e)}')
            ]), quote=message.get(Source).pop(0))  # noqa
            logger.error(f'在数据库写入QQ【{qq}】的第二个白名单时出错: ↓\n{traceback.format_exc()}')
            return
    else:  # main和alt位都满了，联系管理
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('需要被添加白名单的QQ已有两个白名单')
        ]), quote=message.get(Source).pop(0))  # noqa
        return

    try:
        res: str = execute_command(f'whitelist add {real_mc_id}')
    except Exception as e:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'添加白名单时已写入数据库但无法连接到服务器，请联系管理解决: ↓\n{str(e)}')
        ]), quote=message.get(Source).pop(0))  # noqa
        return
    if res.startswith('Added'):
        await app.sendGroupMessage(group, MessageChain.create([
            At(qq), Plain(' 呐呐呐，白名单给你!')
        ]), quote=message.get(Source).pop(0))  # noqa
    else:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'添加白名单时已写入数据库但服务器返回预料之外的内容: ↓\n{res}')
        ]), quote=message.get(Source).pop(0))  # noqa


@PermissionCheck
@LengthCheck(length=4)
async def add_whitelist(*args, message: MessageChain, **kwagrs):
    # if len(args) != 4:
    #     return None
    if args[2].isdigit():  # !wl add 123456 id
        await add_whitelist_to_qq(int(args[2]), args[3], message=message, **kwagrs)
        return 0
    elif message.has(At):  # noqa
        await add_whitelist_to_qq(message.get(At)[0].dict()['target'], args[3], message=message, **kwagrs)  # noqa
        return 0
