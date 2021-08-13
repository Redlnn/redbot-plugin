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

MODULE_NAME = '随机整数'
MODULE_DESC = ''
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = ()


@bcc.receiver('GroupMessage')
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if group.id not in active_group and active_group:
        return 0
    cmd: str = message.asDisplay().strip()  # 如 "!test a bc 3 4d"
    if cmd[0] not in ('!', '！'):
        return 0

    if cmd.startswith('roll'):
        await app.sendGroupMessage(group, MessageChain(__root__=[
            Plain(str(randint(0, 100)))
        ]), quote=message.get(Source).pop(0))  # noqa
