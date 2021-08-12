#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging

from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain, Source, Image)
from miraibot import GetCore

from .info import MODULE_NAME
from .config import read_cfg
from .gen_img import generate_img

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
    cmd: str = message.asDisplay()
    reply_dict = read_cfg()
    for _ in dict(reply_dict['normal']).keys():
        if cmd.lower() == _:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(reply_dict['normal'][_])
            ]), quote=message.get(Source).pop(0))
    for _ in dict(reply_dict['with_img']).keys():
        if cmd.lower() == _:
            img_path = generate_img(reply_dict['with_img'][_])
            try:
                msg_id = await app.sendGroupMessage(group, MessageChain.create([
                    Image.fromLocalFile(img_path)
                ]))
                if msg_id <= 0:
                    logger.warning('发送图片消息失败')
            finally:
                os.remove(img_path)
