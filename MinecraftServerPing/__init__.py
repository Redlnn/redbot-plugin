#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain)

from miraibot import GetCore
from miraibot.command import group_command
from .config import read_cfg
from .info import (MODULE_DESC, MODULE_NAME)
from .ping import ping_client

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME
__plugin_usage__ = MODULE_DESC

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

cfg = read_cfg()

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = cfg['active_group']
if active_group is None:
    active_group = ()


@group_command('!ping', ['！ping'], '获取指定mc服务器的信息', group=active_group)
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    args: list = message.asDisplay().strip()[1:].strip().split(' ')  # 切割命令，结果为 ('test', 'a', 'bc', '3', '4d')
    if len(args) == 1:
        server_address = cfg['default_server']
    elif len(args) == 2:
        if '://' in args[1]:
            await app.sendGroupMessage(group, MessageChain.create([Plain('不支持带有协议前缀的地址')]))
            return None
        server_address = args[1]
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('未知命令，请检查你的输入')]))
        return None

    res = ping_client(server_address)
    if type(res) is str:
        await app.sendGroupMessage(group, MessageChain.create([Plain(res)]))
    else:
        motd_list = res['motd'].split('\n')
        motd = f' | {motd_list[0].strip()}'
        if len(motd_list) == 2:
            motd += f'\n | {motd_list[1].strip()}'
        online_player = int(res['online_player'])
        if online_player == 0:
            msg_send = f'咕咕咕！！！\n服务器版本: [{res["protocol"]}] {res["version"]}\nMOTD:\n{motd}' \
                       f'\n延迟: {res["delay"]}ms\n在线人数: {res["online_player"]}/{res["max_player"]}\nにゃ～'
        else:
            players_list = ''
            for _ in res['player_list']:
                players_list += f' | {_[0]}\n'
            if online_player <= 10:
                msg_send = f'咕咕咕！！！\n服务器版本: [{res["protocol"]}] {res["version"]}\nMOTD:\n{motd}' \
                           f'\n延迟: {res["delay"]}ms\n在线人数: {res["online_player"]}/{res["max_player"]}\n' \
                           f'在线列表：\n{players_list}にゃ～'
            else:
                msg_send = f'咕咕咕！！！\n服务器版本: [{res["protocol"]}] {res["version"]}\nMOTD:\n{motd}' \
                           f'\n延迟: {res["delay"]}ms\n在线人数: {res["online_player"]}/{res["max_player"]}\n' \
                           f'在线列表（不完整）：\n{players_list}にゃ～'

        await app.sendGroupMessage(group, MessageChain.create([Plain(msg_send)]))
