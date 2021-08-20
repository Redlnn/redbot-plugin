#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain, Source, Image)

from miraibot import GetCore
from plugins.Text2Img.gen_img import generate_img
from .config import read_cfg
from .info import MODULE_NAME

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = read_cfg()['active_group']
if active_group is None:
    active_group = ()


@bcc.receiver('GroupMessage')
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if group.id not in active_group and active_group:
        return None
    cmd: str = message.asDisplay().strip()
    if len(cmd) == 0:
        return None
    reply_dict = read_cfg()
    if reply_dict['normal'] is not None:
        for _ in dict(reply_dict['normal']).keys():
            if cmd.lower() == _:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(reply_dict['normal'][_])
                ]), quote=message.get(Source).pop(0))  # noqa
    if reply_dict['with_img'] is not None:
        for _ in dict(reply_dict['with_img']).keys():
            if cmd.lower() == _:
                img_path = generate_img(reply_dict['with_img'][_])
                try:
                    msg_id = await app.sendGroupMessage(group, MessageChain.create([
                        Image.fromLocalFile(img_path)
                    ]))
                    if msg_id.messageId <= 0:
                        logger.warning('发送图片消息失败，可能是被QQ风控了，请不要使用敏感词')
                        await app.sendGroupMessage(group, MessageChain.create([
                            Plain('发送图片消息失败，可能是被QQ风控了，请不要使用敏感词')
                        ]))
                finally:
                    os.remove(img_path)
