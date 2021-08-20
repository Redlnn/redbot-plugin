#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import traceback

from graia.application.entry import (GraiaMiraiApplication, MessageChain, Plain, At, Source, Group)
import requests
import urllib3

from ..api import get_mc_id, get_uuid, is_mc_id, PermissionCheck
from ..info import MODULE_NAME
from .config import read_cfg
from .db import execute_query_sql

from graia.application.exceptions import UnknownTarget

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')
cfg = read_cfg()


async def add_whitelist_to_qq(qq: int, mc_id: str, app: GraiaMiraiApplication, message: MessageChain, group: Group, **kwagrs):
    if not is_mc_id(mc_id):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('你选择的不是一个有效的id')
        ]))
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
    # TODO: 检查id是否已被使用/是否已有白名单


@PermissionCheck
async def add_whitelist(*args, message: MessageChain, **kwagrs):
    if len(args) != 4:
        return None
    if args[2].isdigit():  # !wl add 123456 id
        await add_whitelist_to_qq(int(args[2]), args[3], message=message, **kwagrs)
        return 0
    elif message.has(At):
        await add_whitelist_to_qq(message.get(At)[0].dict()['target'], args[3], message=message, **kwagrs)
        return 0


__all__ = [add_whitelist]
