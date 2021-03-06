#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
识别群内的B站链接、分享、av号、BV号并获取其对应的视频的信息

以下几种消息均可触发
 - 新版B站app分享的小程序
 - 旧版B站app分享的xml消息
 - B站概念版分享的json消息
 - 文字消息里含有B站视频地址，如 https://www.bilibili.com/video/av2
 - 文字消息里含有B站视频地址，如 https://www.bilibili.com/video/BV1xx411c7mD
 - 文字消息里含有B站视频地址，如 https://b23.tv/3V31Ap
 - !BV1xx411c7mD
 - !av2
"""

import json
import logging
import time
from xml.dom.minidom import parseString

import regex
import requests
from graia.application.entry import (App, GraiaMiraiApplication, Group, Image, MessageChain, Plain, Xml)
from requests import get

from miraibot import GetCore
from miraibot.command import group_command

MODULE_NAME = '获取B站视频信息'
MODULE_DESC = '识别群内的B站链接、分享、av号、BV号并获取其对应的视频的信息'
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME
__plugin_usage__ = MODULE_DESC

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = ()

avid_re = '(av|AV)[0-9]{1,}'
bvid_re = '[Bb][Vv]1([0-9a-zA-Z]{2})4[1y]1[0-9a-zA-Z]7([0-9a-zA-Z]{2})'


async def get_video_info(origin_id: str = None, app: GraiaMiraiApplication = None, group: Group = None):
    if regex.match(f'^{avid_re}$', origin_id):
        id_type = 'av'
    elif regex.match(f'^{bvid_re}$', origin_id):
        id_type = 'bv'
    else:
        raise ValueError('不是av/BV号')

    if id_type == 'av':
        url = f'http://api.bilibili.com/x/web-interface/view?aid={origin_id[2:]}'
    else:
        url = f'http://api.bilibili.com/x/web-interface/view?bvid={origin_id}'
    res = get(url).text  # B站api返回json文本

    res_format = json.loads(res)  # 读取json文本为dict对象
    if res_format['code'] != 0:
        error_text = f'B站服务器返回错误：↓\n错误代码：{res_format["code"]}\n错误信息：{res_format["message"]}'
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(error_text)]
        ))
        logger.error(f'在请求{origin_id}的信息时，{error_text}')
        raise ValueError(error_text)

    video_info: dict = res_format['data']  # 若错误代码为0，则读取视频信息

    video_cover_url: str = video_info['pic']  # 封面地址
    video_bvid: str = video_info['bvid']  # BV号
    # video_avid: int = video_info['aid']  # av号
    video_title: str = video_info['title']  # 视频标题
    video_sub_num: int = video_info['videos']  # 视频分P数
    video_pub_date: str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video_info['pubdate']))  # 视频发布时间(时间戳)
    # video_unload_date: int = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video_info['ctime']))  # 视频上传时间(时间戳)
    video_desc: str = regex.sub(r'(\n)+', '\n', video_info['desc'], flags=regex.MULTILINE)  # 视频简介，去除多余空行
    video_duration_s: int = video_info['duration']  # 视频长度（单位：秒）
    video_length_m, video_length_s = divmod(video_duration_s, 60)  # 将总的秒数转换为时分秒格式
    video_length_h, video_length_m = divmod(video_length_m, 60)
    if video_length_h == 0:
        video_length = f'{video_length_m}:{video_length_s}'
    else:
        video_length = f'{video_length_h}:{video_length_m}:{video_length_s}'
    # video_up_mid = video_info['owner']['mid']  # up主mid
    video_up_name: int = video_info['owner']['name']  # up主名称
    video_view: int = video_info['stat']['view']  # 播放量
    video_danmu: int = video_info['stat']['danmaku']  # 弹幕量
    video_like: int = video_info['stat']['like']  # 点赞量
    video_coin: int = video_info['stat']['coin']  # 投币量
    video_favorite: int = video_info['stat']['favorite']  # 收藏量

    if len(video_desc.strip()) > 0:
        video_desc: str = '\n | ' + video_desc.replace('\n', '\n | ')
    else:
        video_desc: str = '-'

    info_text = f'''\
BV号：{video_bvid}
标题：{video_title[:30] + "..." if len(video_title) > 30 else video_title}
简介：{video_desc[:40] + "..." if len(video_desc) > 40 else video_desc}
UP主：{video_up_name}
时长：{video_length}
发布时间：{video_pub_date}
'''
    if video_sub_num > 1:
        info_text += f'分P数量：{video_sub_num}\n'
    info_text += f'{video_view if video_view < 10000 else str(round(video_view / 10000, 1)) + "万"}播放 '
    info_text += f'{video_danmu if video_danmu < 10000 else str(round(video_danmu / 10000, 1)) + "万"}弹幕\n'
    info_text += f'{video_like if video_like < 10000 else str(round(video_like / 10000, 1)) + "万"}点赞 '
    info_text += f'{video_coin if video_coin < 10000 else str(round(video_coin / 10000, 1)) + "万"}投币 '
    info_text += f'{video_favorite if video_favorite < 10000 else str(round(video_favorite / 10000, 1)) + "万"}收藏\n'
    info_text += f'链接：https://www.bilibili.com/video/{video_bvid}'

    return info_text, video_cover_url


@group_command('!BV1xxx4y1x7xx', desc='获取指定BV号的视频信息')
async def register_command_1():
    pass


@group_command('!avxxxxxx', desc='获取指定av号的视频信息')
async def register_command_2():
    pass


@bcc.receiver('GroupMessage')
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain):
    if group.id not in active_group and active_group:
        return
    origin_id: str = None
    if message.has(App):  # noqa
        app_json = message.get(App)[0].content  # noqa
        app_dict = json.loads(app_json)
        try:
            app_id = app_dict['meta']['detail_1']['appid']
        except KeyError:
            try:
                app_id = app_dict['meta']['news']['appid']
            except:  # noqa
                return
        except:  # noqa
            return

        if int(app_id) == 1109937557:
            b23_url = app_dict['meta']['detail_1']['qqdocurl']
        elif int(app_id) == 1105517988:
            b23_url = app_dict['meta']['news']['jumpUrl']
        else:
            return
        res = requests.get(b23_url, allow_redirects=False)
        bli_url = res.headers['Location']
        origin_id = regex.search(bvid_re, bli_url)  # 获得BV号
        if origin_id is None:
            return
        else:
            origin_id = origin_id.group(0)  # noqa
    elif message.has(Xml):  # noqa
        xml_text = message.get(Xml)[0].xml  # noqa
        xml_tree = parseString(xml_text)
        xml_collection = xml_tree.documentElement

        if xml_collection.hasAttribute('url'):
            xml_url = xml_collection.getAttribute('url')
            if 'www.bilibili.com/video/' in xml_url:
                origin_id = regex.search(bvid_re, xml_url)  # 获得BV号
                if origin_id is None:
                    origin_id = regex.search(avid_re, xml_url)  # 获得BV号
                origin_id = origin_id.group(0)  # noqa
            elif 'b23.tv/' in xml_url:
                res = requests.get(xml_url, allow_redirects=False)
                bli_url = res.headers['Location']
                origin_id = regex.search(bvid_re, bli_url)  # 获得BV号
                if origin_id is None:
                    return
                else:
                    origin_id = origin_id.group(0)  # noqa
            else:
                return
        else:
            return
    elif message.has(Plain):  # noqa
        cmd: str = message.asDisplay().strip()  # 如 "BV1S64y1W7ej" 或 "av762147945"
        if len(cmd) == 0:
            return
        if 'www.bilibili.com/video/' in cmd:
            origin_id = regex.search(bvid_re, cmd)  # 获得BV号
            if origin_id is None:
                origin_id = regex.search(avid_re, cmd)  # 获得BV号
            if origin_id is None:
                return
            origin_id = origin_id.group(0)  # noqa
        elif 'b23.tv/' in cmd:
            b23_url = regex.search('b23.tv/[0-9a-zA-Z]*', cmd).group(0)  # 去除多余的类似 "?shareFrom=xxx" 的内容
            res = requests.get(f'https://{b23_url}', allow_redirects=False)  # 获得重定向后的B站地址
            bli_url = res.headers['Location']
            origin_id = regex.search(bvid_re, bli_url)  # 获得BV号
            if origin_id is None:
                return
            else:
                origin_id = origin_id.group(0)  # noqa
        elif cmd[:2].lower() in ('av', 'bv'):
            origin_id: str = cmd
        else:
            return
    else:
        return

    try:
        if origin_id is not None:
            info_text, video_cover_url = await get_video_info(origin_id, app, group)
        else:
            return
    except ValueError:
        return

    try:
        await app.sendGroupMessage(group, MessageChain.create([
            Image.fromNetworkAddress(video_cover_url), Plain(info_text)  # noqa
        ]))
    except:  # noqa
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f'视频封面地址：{video_cover_url}\n' + info_text)
        ]))
