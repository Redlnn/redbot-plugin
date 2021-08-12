#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本插件为测试用插件，部署到生产环境时请记得删除或禁用
"""


import logging

from graia.application.entry import (GraiaMiraiApplication, Group, Friend, MessageChain, Plain, App)  # noqa

from miraibot import GetCore

MODULE_NAME = '测试插件'
MODULE_DESC = ''
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = ()


@bcc.receiver("GroupMessage")
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if group.id not in active_group and active_group:
        return 0
    logger.info(f'接收到的消息链为: ↓\n{message}')

    # cmd: str = message.asDisplay().strip()  # 如 "!test a bc 3 4d"
    # if cmd[0] not in ('!', '！'):
    #     return 0
    # args: list = cmd[1:].strip().split()  # 切割命令，结果为 ('test', 'a', 'bc', '3', '4d')
    # logger.info(f'处理后的命令为: ↓\n{args}')

    # message_id = await app.sendGroupMessage(group, MessageChain.create([Plain('Test')]))
    # logger.info(f'本次发送的消息的ID为：{message_id.messageId}')


@bcc.receiver("FriendMessage")
async def friend_message_listener(app: GraiaMiraiApplication, friend: Friend, message: MessageChain):
    logger.info(f'接收到的消息链为: ↓\n{message}')

    # cmd: str = message.asDisplay().strip()  # 如 "!test a bc 3 4d"
    # if cmd[0] not in ('!', '！'):
    #     return 0
    # args: list = cmd[1:].strip().split()  # 切割命令，结果为 ('test', 'a', 'bc', '3', '4d')
    # logger.info(f'处理后的命令为: ↓\n{args}')

    # message_id = await app.sendGroupMessage(group, MessageChain.create([Plain('Test')]))
    # logger.info(f'本次发送的消息的ID为：{message_id.messageId}')
