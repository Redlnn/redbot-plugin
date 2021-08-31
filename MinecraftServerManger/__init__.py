#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from graia.application.entry import (GraiaMiraiApplication, Group, Member, MemberPerm, MessageChain, Plain)

from miraibot import GetCore
from miraibot.command import group_command
from .config import read_cfg
from .info import (MODULE_DESC, MODULE_NAME)
from .rcon.rcon import execute_command
from .whitelist.utils import check_qq_had_id
from .whitelist.wl_add import add_whitelist
from .whitelist.wl_add import add_whitelist_to_qq
from .whitelist.wl_del import del_whitelist
from .whitelist.wl_info import whitelist_info

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME
__plugin_usage__ = MODULE_DESC

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = read_cfg()['active_group']
if active_group is None:
    active_group = ()

wl_function = {
    'add': add_whitelist,
    'info': whitelist_info,
    'del': del_whitelist
}

wl_menu = '''-----------白名单管理菜单-----------
!wl add [QQ号或@QQ] [游戏ID]  - 【管理】为某个ID绑定QQ并给予白名单
!wl del @QQ  - 【管理】删除某个QQ的所有白名单
!wl del qq [QQ号]  - 【管理】删除某个QQ的所有白名单
!wl del id [游戏ID]  - 【管理】删除某个ID所属QQ的所有白名单
!wl info [@QQ或游戏ID]  - 查询被@QQ或某个ID的信息
!wl info qq [QQ号]  - 查询某个QQ的信息
!wl info id [游戏ID]  - 查询某个ID的信息'''


@group_command('!wl', ['！wl'], '服务器管理-白名单相关', group=active_group)
async def whitelist(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain):
    args: list = message.asDisplay().strip()[1:].strip().split()  # 切割命令，结果为 ('wl', 'a', 'bc', '3', '4d')

    if len(args) == 1:
        return wl_menu
    for _ in wl_function.keys():
        if args[1].lower() == _:
            res = await wl_function[_](*args, app=app, group=group, member=member, message=message)
            if res is None:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain('未知命令，请检查输入是否正确')
                ]))
            elif res is not None and res != 0:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(res)
                ]))
            break


@group_command('!myid', ['！myid'], '服务器管理-自助获取白名单', group=active_group)
async def myid(app: GraiaMiraiApplication, member: Member, message: MessageChain, group: Group):
    args = message.asDisplay().strip()[1:].strip().split()
    if len(args) != 2:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('未知命令，请检查输入是否正确')
        ]))
    if member.permission not in (MemberPerm.Owner, MemberPerm.Administrator):
        res = await check_qq_had_id(member.id, app, message, group)
        if res[1] == 1 or res[1] == 2:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('你已有一个白名单，因此你正在申请第二个白名单，但你没有权限！\n若想删除前一个白名单或想申请小号的白名单请联系管理员')
            ]))
    await add_whitelist_to_qq(member.id, args[1], app, message, group)


@group_command('!list', ['！list'], '服务器管理-获取服务器在线列表', group=active_group)
async def get_player_list(app: GraiaMiraiApplication, group: Group):
    try:
        player_list: str = execute_command('list').split(':')  # noqa
    except Exception as e:
        msg_send = str(e)
    else:
        if player_list[1] == '':
            msg_send = '服务器目前没有在线玩家'
        else:
            playerlist = player_list[0].replace('There are', '服务器在线玩家数: ').replace(' of a max of ', '/')
            playerlist = playerlist.replace('players online', '\n在线列表: ')
            msg_send = playerlist + player_list[1].strip()
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(msg_send)
    ]))


@group_command('!tps', ['！tps'], '服务器管理-获取服务器tps', group=active_group)
async def get_server_tps(app: GraiaMiraiApplication, group: Group):
    try:
        result: str = execute_command('tps')
    except Exception as e:
        msg_send = str(e)
    else:
        result = result.replace('TPS from last 5s, 1m, 5m, 15m', '服务器过去5秒、1分钟、5分钟、15分钟的TPS')
        result = result.replace('TPS from last 1m, 5m, 15m', '服务器过去1分钟、5分钟、15分钟的TPS')
        result = result.replace('Current Memory Usage:', '当前内存使用情况')
        msg_send = result.replace('(Max:', '(最大:')
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(msg_send)
    ]))


@group_command('!mspt', ['！mspt'], '服务器管理-获取服务器mspt', group=active_group)
async def get_server_mspt(app: GraiaMiraiApplication, group: Group):
    try:
        result: str = execute_command('mspt')
    except Exception as e:
        msg_send = str(e)
    else:
        msg_send = result.replace(
                'Server tick times (avg/min/max) from last 5s, 10s, 1m',
                '服务器过去5秒/10秒/1分钟内的mspt (平均/最小/最大)'
        )
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(msg_send)
    ]))


@group_command('!run', ['！run'], '服务器管理-在服务器上运行命令', group=active_group,
               permission=[MemberPerm.Administrator, MemberPerm.Owner])
async def run_server_command(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    command = message.asDisplay().strip()[5:]
    try:
        result = execute_command(command)
    except ValueError as e:
        msg_send = str(e)
    else:
        if result is None:
            msg_send = '服务器返回为空'
        else:
            msg_send = f'服务器返回：↓\n{result}'
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(msg_send)
    ]))
