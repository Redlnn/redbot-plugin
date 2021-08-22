#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import traceback

from graia.application.entry import (GraiaMiraiApplication, MessageChain, Plain, At, Source, Group)
from graia.application.exceptions import UnknownTarget


from ..api import get_uuid, get_mc_id, is_mc_id, get_time, PermissionCheck, LengthCheck
from ..info import MODULE_NAME
from ..rcon.rcon import execute_command
from .config import read_cfg
from .db import execute_query_sql, execute_update_sql
from .utils import check_qq_had_id

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')
cfg = read_cfg()


async def del_whitelist_from_id(mc_id: str, app: GraiaMiraiApplication, message: MessageChain, group: Group, **kwargs):
    pass


async def del_whitelist_from_qq(qq: int, app: GraiaMiraiApplication, message: MessageChain, group: Group, **kwargs):
    had_status = check_qq_had_id(qq, app, message, group)
    if had_status[0] == 'error':  # 检查该QQ是否已经申请白名单
        return  # 出错了
    elif had_status[0] == 'null':  # main和alt位均为空
        try:
            await app.sendGroupMessage(group, MessageChain.create([
                At(qq),
                Plain(f' ({qq}) 好像一个白名单都没有呢~')
            ]))
        except UnknownTarget:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'{qq} 好像一个白名单都没有呢~')
            ]))
        return
    elif had_status[1] == 1 or had_status[1] == 2:  # alt位为空
        delete_sql = f'delete from {cfg["table"]} where qq={qq}'
        try:
            execute_update_sql(delete_sql)
        except Exception as e:  # noqa
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'在数据库删除QQ【{qq}】的白名单时出错: ↓\n{str(e)}')
            ]))
            logger.error(f'在数据库删除QQ【{qq}】的白名单时出错: ↓\n{traceback.format_exc()}')
            return
        try:
            mc_id = get_mc_id(had_status[0])
        except Exception as e:  # noqa
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'无法查询【{had_status[0]}】对应的正版id: ↓\n{str(e)}')
            ]))
            logger.error(f'无法查询【{had_status[0]}】对应的正版id: ↓\n{traceback.format_exc()}')
        else:
            result = execute_command(f'whitelist remove {mc_id}')
            if result.startswith('Removed '):
                try:
                    await app.sendGroupMessage(group, MessageChain.create([
                        At(qq),
                        Plain(f' ({qq}) 的白名单都删掉啦~')
                    ]))
                except UnknownTarget:
                    await app.sendGroupMessage(group, MessageChain.create([
                        Plain(f'{qq} 的白名单都删掉啦~')
                    ]))
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(f'从服务器删除id为【{mc_id}】的白名单时，服务器返回意料之外的内容：↓\n{result}')
                ]))
        return
    else:
        delete_sql = f'delete from {cfg["table"]} where qq={qq}'
        try:
            execute_update_sql(delete_sql)
        except Exception as e:  # noqa
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'在数据库删除QQ【{qq}】的白名单时出错: ↓\n{str(e)}')
            ]))
            logger.error(f'在数据库删除QQ【{qq}】的白名单时出错: ↓\n{traceback.format_exc()}')
            return
        flag = []
        try:
            mc_id_1 = get_mc_id(had_status[0])
        except Exception as e:  # noqa
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'无法查询【{had_status[0]}】对应的正版id: ↓\n{str(e)}')
            ]))
            logger.error(f'无法查询【{had_status[0]}】对应的正版id: ↓\n{traceback.format_exc()}')
        else:
            result = execute_command(f'whitelist remove {mc_id_1}')
            if result.startswith('Removed '):
                flag.append(True)
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(f'从服务器删除id为【{mc_id_1}】的白名单时，服务器返回意料之外的内容：↓\n{result}')
                ]))
                flag.append(False)

        try:
            mc_id_2 = get_mc_id(had_status[1])
        except Exception as e:  # noqa
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'无法查询【{had_status[0]}】对应的正版id: ↓\n{str(e)}')
            ]))
            logger.error(f'无法查询【{had_status[0]}】对应的正版id: ↓\n{traceback.format_exc()}')
        else:
            result = execute_command(f'whitelist remove {mc_id_1}')
            if result.startswith('Removed '):
                flag.append(True)
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(f'从服务器删除id为【{mc_id_2}】的白名单时，服务器返回意料之外的内容：↓\n{result}')
                ]))
                flag.append(False)

        if (flag[0] and not flag[1]) or (flag[1] and not flag[0]):
            try:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain('只从服务器上删除了 '),
                    At(qq),
                    Plain(f' ({qq}) 的部分白名单')
                ]))
            except UnknownTarget:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(f'只从服务器上删除了 {qq} 的白名单都删掉啦~')
                ]))
        else:
            try:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(qq),
                    Plain(f' ({qq}) 的白名单都删掉啦~')
                ]))
            except UnknownTarget:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(f'{qq} 的白名单都删掉啦~')
                ]))
        return



@PermissionCheck
@LengthCheck(length=4)
async def del_whitelist(*args, message: MessageChain, **kwagrs):
    # if len(args) != 4:
    #     return None
    if args[2] == 'qq':
        if args[3].isdigit():  # !wl del qq 123456
            await del_whitelist_from_qq(int(args[2]), message=message, **kwagrs)
            return 0
        elif message.has(At):  # !wl del qq @body
            await del_whitelist_from_qq(message.get(At)[0].dict()['target'], message=message, **kwagrs)
            return 0
        else:
            return
    elif args[2] == 'id':
        if not is_mc_id(args[3]):
            return
        await del_whitelist_from_id(args[3], message=message, **kwagrs)
    else:
        return
