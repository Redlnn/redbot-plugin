#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
根据av号或BV号获取B站视频信息，消息最前面加感叹号

用法：在本Bot账号所在的任一一QQ群中发送 av号 或 BV号 均可触发本插件功能
"""

import json
import logging
import time

import regex
import requests
from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Plain, Image, App)
from requests import get

from miraibot import GetCore

MODULE_NAME = '获取B站视频信息'
MODULE_DESC = ''
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = ()

avid_re = '^av[0-9]{1,}$'
bvid_re = '^(BV|bv)(1)[0-9a-zA-Z]{2}(4)[1y]{1}(1)[0-9a-zA-Z]{1}(7)[0-9a-zA-Z]{2}$'


async def get_video_info(origin_id: str = None, app: GraiaMiraiApplication = None, group: Group = None):
    id_type = None
    if regex.match(avid_re, origin_id):
        id_type = 0
    elif regex.match(bvid_re, origin_id):
        id_type = 1
    else:
        raise ValueError('不是av/BV号')

    if id_type is None:
        return 0
    if id_type == 0:
        url = f'http://api.bilibili.com/x/web-interface/view?aid={origin_id[2:]}'
    else:
        url = f'http://api.bilibili.com/x/web-interface/view?bvid={origin_id}'
    res = get(url).text

    res_format = json.loads(res)
    if res_format['code'] != 0:
        error_text = f'B站服务器返回错误：↓\n错误代码：{res_format["code"]}\n错误信息：{res_format["message"]}'
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(error_text)]
        ))
        logger.error(error_text)
        raise ValueError(error_text)

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

    info_text = f'BV号：{video_bvid}\nav号：av{video_avid}'
    if len(video_title) > 20:
        info_text += f'\n标题：{video_title[:20]}...\n'
    else:
        info_text += f'\n标题：{video_title}\n'

    video_desc = video_desc.split('\n', 1)[0]
    if len(video_desc) > 25:
        info_text += f'简介：{video_desc[:25]}...\n'
    else:
        info_text += f'简介：{video_desc}\n'

    if video_sub_num > 1:
        info_text += f'分P：{video_sub_num}\n'

    info_text += f'时长：{video_length}\nUP主：{video_up_name}\n发布时间：{video_pub_date}\n'
    if int(video_view) > 9999:
        video_view = round(int(video_view) / 10000, 1)
        info_text += f'播放：{video_view}万 '
    else:
        info_text += f'播放：{video_view} '
    if int(video_danmu) > 9999:
        video_danmu = round(int(video_danmu) / 10000, 1)
        info_text += f'弹幕：{video_danmu}万\n'
    else:
        info_text += f'弹幕：{video_danmu}\n'
    if int(video_like) > 9999:
        video_like = round(int(video_like) / 10000, 1)
        info_text += f'点赞：{video_like}万 '
    else:
        info_text += f'点赞：{video_like} '
    if int(video_coin) > 9999:
        video_coin = round(int(video_coin) / 10000, 1)
        info_text += f'投币：{video_coin}万 '
    else:
        info_text += f'投币：{video_coin} '
    if int(video_favorite) > 9999:
        video_favorite = round(int(video_favorite) / 10000, 1)
        info_text += f'收藏：{video_favorite}万\n'
    else:
        info_text += f'收藏：{video_favorite}\n'
    info_text += f'链接：https://www.bilibili.com/video/{video_bvid}'

    return info_text, video_cover_url


@bcc.receiver("GroupMessage")
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if group.id not in active_group and active_group:
        return 0
    if message.has(App):  # noqa
        app_json = message.get(App)[0].content  # noqa
        app_dict = json.loads(app_json)
        try:
            app_id = app_dict['meta']['detail_1']['appid']
            if app_id == '1109937557':
                b23_url_with_other = app_dict['meta']['detail_1']['qqdocurl']
                try:
                    b23_url = regex.match('^(http|https)://b23.tv/[0-9a-zA-Z]*[?]', b23_url_with_other).group(0)[:-1]
                except AttributeError:
                    return 0
                res = requests.get(b23_url, allow_redirects=False)
                bli_url_with_other = res.headers['Location']
                origin_id = regex.search(bvid_re[1:-1], bli_url_with_other).group(0)  # 获得BV号
            else:
                return 0
        except:  # noqa
            return 0
    elif message.has(Plain):  # noqa
        cmd: str = message.asDisplay().strip()  # 如 "!BV1S64y1W7ej" 或 "!av762147945"
        if cmd[0] not in ('!', '！'):
            return 0
        origin_id: str = cmd[1:].strip()
        # origin_id: str = cmd.strip()
    else:
        return 0

    try:
        info_text, video_cover_url = await get_video_info(origin_id, app, group)
    except ValueError as e:
        error_text = str(e)
        if error_text.startswith('B站服务器返回错误'):
            info_text = error_text
            return 0
        else:
            return 0

    try:
        await app.sendGroupMessage(group, MessageChain.create([
            Image.fromNetworkAddress(video_cover_url), Plain(info_text)  # noqa
        ]))
    except:  # noqa
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'视频封面地址：{video_cover_url}\n' + info_text)
        ]))
