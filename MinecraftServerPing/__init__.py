#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain)

from miraibot import GetCore
from .config import read_cfg
from .info import MODULE_NAME
from .ping import ping_client

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

cfg = read_cfg()

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = cfg['active_group']
if active_group is None:
    active_group = ()


@bcc.receiver('GroupMessage')
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if group.id not in active_group and active_group:
        return 0
    cmd: str = message.asDisplay().strip()  # 如 "!test a bc 3 4d"
    if cmd[0] not in ('!', '！'):
        return 0
    args: list = cmd[1:].strip().split(' ')  # 切割命令，结果为 ('test', 'a', 'bc', '3', '4d')
    if args[0] != 'ping':
        return 0
    if len(args) == 1:
        server_address = cfg['default_server']
    elif len(args) == 2:
        if '://' in args[1]:
            await app.sendGroupMessage(group, MessageChain.create([Plain('不支持带有协议前缀的地址')]))
            return 0
        server_address = args[1]
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('未知命令，请检查你的输入')]))
        return 0

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
            msg_send = f'咕咕咕！！！\n服务器版本: [{res["protocol"]}] {res["version"]}\nMOTD:\n{motd}'\
                       f'\n延迟: {res["delay"]}ms\n在线人数: {res["online_player"]}/{res["max_player"]}\nにゃ～'
        else:
            players_list = ''
            for _ in res['player_list']:
                players_list += f' | {_[0]}\n'
            if online_player <= 10:
                msg_send = f'咕咕咕！！！\n服务器版本: [{res["protocol"]}] {res["version"]}\nMOTD:\n{motd}'\
                           f'\n延迟: {res["delay"]}ms\n在线人数: {res["online_player"]}/{res["max_player"]}\n'\
                           f'在线列表：\n{players_list}にゃ～'
            else:
                msg_send = f'咕咕咕！！！\n服务器版本: [{res["protocol"]}] {res["version"]}\nMOTD:\n{motd}'\
                           f'\n延迟: {res["delay"]}ms\n在线人数: {res["online_player"]}/{res["max_player"]}\n'\
                           f'在线列表（不完整）：\n{players_list}にゃ～'

        await app.sendGroupMessage(group, MessageChain.create([Plain(msg_send)]))
