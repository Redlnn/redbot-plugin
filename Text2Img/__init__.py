#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain, Image)

from miraibot import GetCore
from .config import read_cfg
from .gen_img import generate_img
from .info import MODULE_NAME

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = read_cfg()['active_group']
if active_group is None:
    active_group = ()


@bcc.receiver("GroupMessage")
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if group.id not in active_group and active_group:
        return 0
    cmd: str = message.asDisplay().strip()  # 如 "!test a bc 3 4d"
    if cmd[0] not in ('!', '！'):
        return 0
    args: list = cmd[1:].strip().split(' ', 1)  # 切割命令，结果为 ('test', 'a', 'bc', '3', '4d')
    if args[0] != 'img':
        return 0
    img_path = generate_img(args[1])
    try:
        msg_id = await app.sendGroupMessage(group, MessageChain.create([
            Image.fromLocalFile(img_path)
        ]))
        if msg_id.messageId <= 0:
            logger.warning('发送图片消息失败')
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('发送图片消息失败，可能是被QQ风控了，请不要使用敏感词')
        ]))
    finally:
        os.remove(img_path)
