#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from graia.application.entry import (GraiaMiraiApplication, Group, Image, MessageChain, Plain)

from miraibot import GetCore
from miraibot.command import group_command
from .config import read_cfg
from .gen_img import generate_img
from .info import (MODULE_DESC, MODULE_NAME)

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME
__plugin_usage__ = MODULE_DESC

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = read_cfg()['active_group']
if active_group is None:
    active_group = ()


@group_command('!img', ['！img'], '将文字转为图片', group=active_group)
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    args: list = message.asDisplay().strip()[1:].strip().split(' ', 1)  # 切割命令，结果为 ('test', 'a', 'bc', '3', '4d')
    if len(args) < 2:
        return
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
