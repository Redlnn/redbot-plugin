#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
根据av号或BV号获取B站视频信息，消息最前面加感叹号

用法：在本Bot账号所在的任一一QQ群中发送 av号 或 BV号 均可触发本插件功能
"""

import logging
import time
from json import loads

import regex
from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain)
from graia.application.message.elements.internal import Image
from requests import get

from miraibot import GetCore

bcc = GetCore.bcc()
__plugin_name__ = __name__ = '获取B站视频信息'

logger = logging.getLogger(f'MiraiBot.{__name__}')

avid_re = '^av[0-9]{1,}$'
bvid_re = '^(BV|bv)(1)[0-9a-zA-Z]{2}(4)[1y](1)[0-9a-zA-Z]{1}(7)[0-9a-zA-Z]{2}$'


@bcc.receiver("GroupMessage")
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    cmd: str = message.asDisplay().strip()  # 如 "!BV1S64y1W7ej" 或 "!av762147945"
    if cmd[0] not in ('!', '！'):
        return 0
    origin_id: str = cmd[1:].strip()
    # origin_id: str = cmd.strip()
    id_type = None
    if regex.match(avid_re, origin_id):
        id_type = 0
    elif regex.match(bvid_re, origin_id):
        id_type = 1

    if id_type is None:
        return 0
    if id_type == 0:
        url = f'http://api.bilibili.com/x/web-interface/view?aid={origin_id[2:]}'
    else:
        url = f'http://api.bilibili.com/x/web-interface/view?bvid={origin_id}'
    res = get(url).text

    res_format = loads(res)
    if res_format['code'] != 0:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'B站服务器返回错误：↓\n错误代码：{res_format["code"]}\n错误信息：{res_format["message"]}')]
        ))
        logger.error(f'B站服务器返回错误：↓\n错误代码：{res_format["code"]}\n错误信息：{res_format["message"]}')
        return 0

    video_info = res_format['data']

    video_cover_url = video_info['pic']
    video_bvid = video_info['bvid']
    video_avid = video_info['aid']
    video_title = video_info['title']
    video_sub_num = video_info['videos']
    video_pub_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video_info['pubdate']))
    video_desc = video_info['desc']
    video_duration_s = video_info['duration']
    video_length_m, video_length_s = divmod(video_duration_s, 60)
    video_length_h, video_length_m = divmod(video_length_m, 60)
    if video_length_h == 0:
        video_length = f'{video_length_m}:{video_length_s}'
    else:
        video_length = f'{video_length_h}:{video_length_m}:{video_length_s}'
    # video_up_mid = video_info['owner']['mid']  # up主mid
    video_up_name = video_info['owner']['name']
    video_view = video_info['stat']['view']
    video_danmu = video_info['stat']['danmaku']
    video_like = video_info['stat']['like']
    video_coin = video_info['stat']['coin']
    video_favorite = video_info['stat']['favorite']

    info_text = f'''BV号：{video_bvid}
av号：av{video_avid}
标题：{video_title}'''

    video_desc = video_desc.split('\n', 1)[0]
    if len(video_desc) > 30:
        info_text += f'\n简介：{video_desc[:30]}...\n'
    else:
        info_text += f'\n简介：{video_desc}\n'

    if video_sub_num > 1:
        info_text += f'分P：{video_sub_num}\n'

    info_text += f'''时长：{video_length}
UP主：{video_up_name}
发布时间：{video_pub_date}
播放：{video_view} 弹幕：{video_danmu}
点赞：{video_like} 投币：{video_coin} 收藏：{video_favorite}
链接：https://www.bilibili.com/video/{video_bvid}'''
    try:
        await app.sendGroupMessage(group, MessageChain.create([
            Image.fromNetworkAddress(video_cover_url), Plain(info_text)
        ]))
    except:  # noqa
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'视频封面地址：{video_cover_url}\n' + info_text)
        ]))
