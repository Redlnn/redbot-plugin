#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import traceback
from typing import Union

from graia.application.entry import (GraiaMiraiApplication, MessageChain, Plain, Source, Group)

from .config import read_cfg
from .db import execute_query_sql
from ..info import MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')
cfg = read_cfg()


async def check_qq_had_id(
        qq: int, app: GraiaMiraiApplication, message: MessageChain, group: Group
) -> Union[tuple[str, None], tuple[str, int], tuple[str, str]]:
    query_sql = f'select main_uuid, alt_uuid from {cfg["table"]} where qq={qq};'
    try:
        res = execute_query_sql(query_sql)
    except Exception as e:  # noqa
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'在数据库查询QQ【{qq}】是否已有白名单时出错: ↓\n{str(e)}')
        ]), quote=message.get(Source).pop(0))  # noqa
        logger.error(f'在数据库查询QQ【{qq}】是否已有白名单时出错: ↓\n{traceback.format_exc()}')
        return 'error', None

    if res is None:
        return 'null', None  # 两个位置均为空
    elif res[0] and not res[1]:
        return res[0], 1  # main位置为空
    elif res[1] and not res[0]:
        return res[1], 2  # alt位置为空
    else:
        return res[0], res[1]  # 两个位置均不为空
