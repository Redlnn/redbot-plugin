#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
搜索我的世界中文Wiki

用法：在下面的 active_group 变量中的QQ群内发送【!wiki {关键词}】即可
"""

import json
import logging
from random import uniform
from time import sleep
from urllib.parse import quote

from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain, Source, App)

from miraibot import GetCore

MODULE_NAME = '我的世界中文Wiki搜索'
MODULE_DESC = ''
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = ()


@bcc.receiver('GroupMessage')
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if group.id not in active_group and active_group:
        return 0
    cmd: str = message.asDisplay().strip()  # 如 "!BV1S64y1W7ej" 或 "!av762147945"
    if cmd[0] not in ('!', '！'):
        return 0
    args: list = cmd[1:].strip().split(' ', 1)
    if len(args) < 2:
        return 0
    search_parm: str = quote(args[1], encoding='utf-8')
    bilibili_wiki_json = {
        'app': 'com.tencent.structmsg',
        'desc': '新闻',
        'view': 'news',
        'ver': '0.0.0.1',
        'prompt': '',
        'meta': {
            'news': {
                'title': f'Biligame Wiki: {args[1]}',
                'desc': f'{args[1]} - Biligame Wiki for Minecraft，哔哩哔哩游戏',
                'preview': 'https://s1.hdslb.com/bfs/static/game-web/duang/mine/asserts/contact.404066f.png',
                'tag': 'Red_lnn Bot',
                'jumpUrl': f'https://searchwiki.biligame.com/mc/index.php?search={str(search_parm)}',
                'appid': 100446242,
                'app_type': 1,
                'action': '',
                'source_url': '',
                'source_icon': '',
                'android_pkg_name': ''
            }
        }
    }
    # gamepedia_wiki_json = {
    #     'app': 'com.tencent.structmsg',
    #     'desc': '新闻',
    #     'view': 'news',
    #     'ver': '0.0.0.1',
    #     'prompt': '',
    #     'meta': {
    #             'news': {
    #                 'title': f'Minecraft Wiki: {args[1]}',
    #                 'desc': f'{args[1]} - Minecraft Wiki，最详细的官方我的世界百科',
    #                 'preview': 'https://images.wikia.com/minecraft_zh_gamepedia/images/b/bc/Wiki.png',
    #                 'tag': 'Red_lnn Bot',
    #                 'jumpUrl': f'https://minecraft-zh.gamepedia.com/index.php?search={str(search_parm)}',
    #                 'appid': 100446242,
    #                 'app_type': 1,
    #                 'action': '',
    #                 'source_url': '',
    #                 'source_icon': '',
    #                 'android_pkg_name': ''
    #             }
    #         }
    # }
    fandom_gamepedia_wiki_json = {
        'app': 'com.tencent.structmsg',
        'desc': '新闻',
        'view': 'news',
        'ver': '0.0.0.1',
        'prompt': '',
        'meta': {
            'news': {
                'title': f'Minecraft Wiki: {args[1]}',
                'desc': f'{args[1]} - Minecraft Wiki，最详细的官方我的世界百科',
                'preview': 'https://images.wikia.com/minecraft_zh_gamepedia/images/b/bc/Wiki.png',
                'tag': 'Red_lnn Bot',
                'jumpUrl': f'https://minecraft.fandom.com/zh/index.php?search={str(search_parm)}',
                'appid': 100446242,
                'app_type': 1,
                'action': '',
                'source_url': '',
                'source_icon': '',
                'android_pkg_name': ''
            }
        }
    }
    msg_id1 = await app.sendGroupMessage(group, MessageChain.create([
        App(content=json.dumps(bilibili_wiki_json), type='App')
    ]))
    sleep(round(uniform(0.3, 0.9), 2))
    msg_id2 = await app.sendGroupMessage(group, MessageChain.create([
        App(content=json.dumps(fandom_gamepedia_wiki_json), type='App')
    ]))

    if msg_id1.messageId <= 0 or msg_id2.messageId <= 0:
        bilibili_wiki = 'https://searchwiki.biligame.com/mc/index.php?search=' + str(search_parm)
        fandom_gamepedia_wiki = 'https://minecraft.fandom.com/zh/index.php?search=' + str(search_parm)
        logging.error('部分Json消息发送失败，转为发送文本')
        msg_send = f'部分Json消息发送失败，转为发送文本\n - 官方wiki: {fandom_gamepedia_wiki}\n - B站镜像wiki: {bilibili_wiki}'
        await app.sendGroupMessage(group, MessageChain.create([Plain(msg_send)]),
                                   quote=message.get(Source).pop(0))  # noqa
