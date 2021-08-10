#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用法：

在本Bot账号所在的任一一QQ群中发送 `!roll` 或 `!roll {任意字符}` 均可触发本插件功能
触发后会回复一个由0至100之间的任一随机整数
"""

import logging
from random import randint

from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain, Source)

from miraibot import GetCore

bcc = GetCore.bcc()
__plugin_name__ = __name__ = '随机整数'

logger = logging.getLogger(f'MiraiBot.{__name__}')


@bcc.receiver("GroupMessage")
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    cmd: str = message.asDisplay().strip()  # 如 "!test a bc 3 4d"
    if cmd[0] not in ('!', '！'):
        return 0
    args = cmd[1:].strip().split()  # 切割命令，结果为 ('test', 'a', 'bc', '3', '4d')
    logger.debug(f'处理后的命令为: ↓\n{args}')

    if args[1].lower() == 'roll':
        await app.sendGroupMessage(group, MessageChain(__root__=[
            Plain(str(randint(0, 100)))
        ]), quote=message.get(Source).pop(0))  # noqa
