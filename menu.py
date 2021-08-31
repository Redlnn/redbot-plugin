#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import regex
from graia.application.entry import (GraiaMiraiApplication, Group, Image, MessageChain)

from miraibot import GetCore
from miraibot.command import (get_group_commands, group_command)
from plugins.Text2Img.gen_img import generate_img

MODULE_NAME = '命令菜单'
MODULE_DESC = ''
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME
__plugin_usage__ = MODULE_DESC


@group_command('!menu', ['！menu', '!help', '！help'])
async def group_message_listener(app: GraiaMiraiApplication, group: Group):
    msg_send = '当前群组可用命令：\n'
    for command, target in get_group_commands().items():
        active_group = regex.search('([0-9]{6,9}|null)$', command).group(0)
        cmd = command[:-len(active_group) - 1]
        if target.Is_alias:
            continue
        if cmd == '!menu':
            continue
        if active_group != group.id and active_group != 'null':
            continue
        if target.Desc == 'null':
            msg_send += f'{cmd}\n'
        else:
            msg_send += f'{cmd} — {target.Desc}\n'
    img_path = generate_img(msg_send.rstrip())
    await app.sendGroupMessage(group, MessageChain.create([
        Image.fromLocalFile(img_path)
    ]))
    os.remove(img_path)
