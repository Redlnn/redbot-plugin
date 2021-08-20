#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from graia.application.entry import (GraiaMiraiApplication, Group, Member, MessageChain, Plain)
from miraibot import GetCore

from .config import read_cfg
from .info import MODULE_NAME
from .whitelist.wl_info import whitelist_info
from .whitelist.wl_add import add_whitelist
from .api import PermissionCheck
from .rcon.rcon import execute_command

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = read_cfg()['active_group']
if active_group is None:
    active_group = ()

wl_function = {
    'add': add_whitelist,
    'info': whitelist_info,
    'del': None
}


async def whitelist(*args, **kwargs):
    for _ in wl_function.keys():
        if args[1].lower() == _:
            return await wl_function[_](*args, **kwargs)
    return


async def get_player_list(*args, **kwargs):
    try:
        player_list = execute_command('list').split(':')
    except ValueError as e:
        return str(e)
    if player_list[1] == '':
        return '服务器目前没有在线玩家'
    else:
        playerlist = player_list[0].replace('There are', '服务器在线玩家数: ').replace(' of a max of ', '/')
        playerlist = playerlist.replace('players online', '\n在线列表: ')
        return playerlist + player_list[1].strip()


async def get_server_tps(*args, **kwargs):
    try:
        result = execute_command('tps')
    except ValueError as e:
        return str(e)
    result = result.replace('TPS from last 5s, 1m, 5m, 15m', '服务器过去5秒、1分钟、5分钟、15分钟的TPS')
    result = result.replace('TPS from last 1m, 5m, 15m', '服务器过去1分钟、5分钟、15分钟的TPS')
    result = result.replace('Current Memory Usage:', '当前内存使用情况')
    return result.replace('(Max:', '(最大:')


async def get_server_mspt(*args, **kwargs):
    try:
        result = execute_command('tps')
    except ValueError as e:
        return str(e)
    return result.replace('Server tick times (avg/min/max) from last 5s, 10s, 1m', '服务器过去5秒/10秒/1分钟内的mspt (平均/最小/最大)')


@PermissionCheck
async def run_server_command(*args, **kwargs):
    command = kwargs['message'].asDisplay().strip()[6:]
    try:
        result = execute_command(command)
    except ValueError as e:
        return str(e)
    if result is None:
        return '服务器返回为空'
    else:
        return f'服务器返回：↓\n{result}'


function_dict = {
    'wl': whitelist,
    'myid': None,
    'list': get_player_list,
    'tps': get_server_tps,
    'mspt': get_server_mspt,
    'run': run_server_command
}


@bcc.receiver("GroupMessage")
async def group_msg_listener(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain):
    if group.id not in active_group and active_group:
        return None
    cmd: str = message.asDisplay().strip()  # 如 "!test a bc 3 4d"
    if len(cmd) == 0 or cmd[0] not in ('!', '！'):
        return None
    args: tuple = cmd[1:].strip().split()  # 切割命令，结果为 ('test', 'a', 'bc', '3', '4d')

    for _ in function_dict.keys():
        if args[0].lower() == _:
            stat = await function_dict[_](*args, app=app, group=group, member=member, message=message)
            if stat is None:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain('未知命令，请检查输入是否正确')
                ]))
            elif stat is not None and stat != 0:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(stat)
                ]))
            break
