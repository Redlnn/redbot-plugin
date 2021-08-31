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
from miraibot.command import group_command

MODULE_NAME = '随机整数'
MODULE_DESC = ''
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
bot = GetCore.bot()
__plugin_name__ = __name__ = MODULE_NAME
__plugin_usage__ = MODULE_DESC

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = ()


@group_command('!roll', ['！roll'], '获取 0-100 的随机数', group=active_group, shell_like=False)
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    await app.sendGroupMessage(
            group,
            MessageChain.create([Plain(str(randint(0, 100)))]),
            quote=message.get(Source).pop(0)  # noqa
    )
