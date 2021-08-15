#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import time

import numpy as np
import regex
from PIL import Image, ImageDraw, ImageFont

from .config import read_cfg
from .info import MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

cfg = read_cfg()


def __get_text_config() -> dict:
    """
    获取正文配置
    """
    ttf_path: str = os.path.join(os.getcwd(), 'plugins', 'fonts',
                                 cfg['text_to_img']['text_config']['font_name'])  # 字体文件的路径
    if not os.path.exists(ttf_path):
        raise ValueError(f'文本转图片所用的字体文件不存在，尝试访问的路径如下：↓\n{ttf_path}')
    font_size: int = cfg['text_to_img']['text_config']['font_size']  # 字体大小
    font_color: str = cfg['text_to_img']['text_config']['font_color']  # 字体颜色
    line_space: int = cfg['text_to_img']['text_config']['line_space']  # 行间距
    margin: int = cfg['text_to_img']['text_config']['margin']  # 上下左右距离内框的间距
    text_config = {
        'ttf_path': ttf_path,
        'font_size': font_size,
        'font_color': font_color,
        'line_space': line_space,
        'margin': margin
    }
    # text_config = {
    #     'ttf_path': os.path.join('OPPOSans'),
    #     'font_size': 50,
    #     'font_color': '#645647',
    #     'line_space': 30,
    #     'side_margin': 80,
    #     'top_margin': 80,
    #     'bottom_margin': 80
    # }
    return text_config


def __get_background_config() -> dict:
    """
    获取背景配置
    """
    background_color: str = cfg['text_to_img']['background_config']['background_color']  # 背景颜色
    box_side_margin: int = cfg['text_to_img']['background_config']['box_side_margin']  # 外框距左右边界距离
    box_top_margin: int = cfg['text_to_img']['background_config']['box_top_margin']  # 外框距上边界距离
    box_bottom_margin: int = cfg['text_to_img']['background_config']['box_bottom_margin']  # 外框距下边界距离
    box_interval: int = cfg['text_to_img']['background_config']['box_interval']  # 内外框距离
    wrap_width: int = cfg['text_to_img']['background_config']['wrap_width']  # 小正方形边长
    outline_width: int = cfg['text_to_img']['background_config']['outline_width']  # 边框厚度
    outline_color: str = cfg['text_to_img']['background_config']['outline_color']  # 边框颜色
    background_config = {
        'background_color': background_color,
        'box_side_margin': box_side_margin,
        'box_top_margin': box_top_margin,
        'box_bottom_margin': box_bottom_margin,
        'box_interval': box_interval,
        'wrap_width': wrap_width,
        'outline_width': outline_width,
        'outline_color': outline_color
    }
    # background_config = {
    #     'background_color': '#fffcf6',
    #     'box_side_margin': 50,
    #     'box_top_margin': 70,
    #     'box_bottom_margin': 250,
    #     'box_interval': 8,
    #     'wrap_width': 8,
    #     'outline_width': 4,
    #     'outline_color': '#fffcf6'
    # }
    return background_config


def __get_time(mode: int = 1) -> str:
    """
    返回当前时间
    """
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    if mode == 2:
        dt = time.strftime("%Y-%m-%d_%H-%M-%S", time_local)
    else:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt


def __is_cjk_char(char: str = None) -> bool:
    """
    判断是否为中日韩字符
    """
    return True if regex.match(r'[\u2100-\u2BFF\u2E80-\u9FFF\uF900-\uFAFF\uFE30-\uFE4F\uFF01-\uFF64\uFFE0-\uFFE7]',
                               char) else False


def __cut_str2list(text: str = None, cut_len: int = None) -> list:
    """
    将超长的字符串切为列表

    :param text: 要被切的字符串
    :param cut_len: 每行字数
    """
    if text == '':
        return ['']
    cut_result_list = []
    ascii_len = 0
    temp_str = ''
    for _ in text:
        if __is_cjk_char(_):
            ascii_len += 2
        else:
            ascii_len += 1
        temp_str += _
        if ascii_len < (cut_len * 2):
            continue
        cut_result_list.append(temp_str)
        temp_str = ''
        ascii_len = 0
    if temp_str != '':
        cut_result_list.append(temp_str)
    del temp_str
    del ascii_len
    return cut_result_list


# def __cut_str(text: str, cut_len: int) -> str:
#     temp_str = ''
#     for _ in text.split('\n'):
#         for __ in __cut_str2list(_, cut_len):
#             temp_str += f'{__}\n'
#     return temp_str


# def __cut(obj, cut_len: int) -> list:
#     return [obj[i:i+cut_len] for i in range(0, len(obj), cut_len)] if obj != '' else ['']


def __ascii_len(text: str = None) -> int:  # 非Ascii字符按两个字符算
    len_txt = len(text)
    len_txt_utf8 = len(text.encode('utf-8'))
    return int((len_txt_utf8 - len_txt) / 2 + len_txt)


def generate_img(text: str = None) -> str:
    """
    根据输入的文本，生成一张图并返回图片文件的路径

    :param text: 文本
    :return: 图片文件的路径
    """
    text_config = __get_text_config()
    bg_config = __get_background_config()
    font = ImageFont.truetype(text_config['ttf_path'], text_config['font_size'])  # 确定正文用的ttf字体
    extra_font = ImageFont.truetype(text_config['ttf_path'],
                                    text_config['font_size'] - int(0.3 * text_config['font_size']))  # 确定而额外文本用的ttf字体
    extra_text1 = '由 Red_lnn 的 Bot 生成'  # 额外文本1
    extra_text2 = __get_time()  # 额外文本2
    text_list = []
    for _ in text.split('\n'):
        text_list.extend(__cut_str2list(_, 20))
    lines = len(text_list)  # 获取行数
    longest_text = ''
    tmp = 0
    for _ in text_list:  # 获取最长的一行
        size = __ascii_len(_)
        if tmp < size:
            longest_text = _
            tmp = size
    del tmp
    longest_line_width, line_height = font.getsize(longest_text)  # 获取最长的那一行的宽高
    extra_text1_width = extra_font.getlength(extra_text1)  # 获取最长的那一行的宽
    extra_text2_width = extra_font.getlength(extra_text2)  # 获取最长的那一行的宽
    if longest_line_width < extra_text1_width:
        longest_line_width = int(extra_text1_width)  # 获取最长的那一行的宽
    if longest_line_width < extra_text2_width:
        longest_line_width = int(extra_text2_width)  # 获取最长的那一行的宽
    line_height += text_config['line_space']  # 加入行距
    # 画布高度 = ((行高 + 行距) * 行数) - 行距 + (2 * 正文边距) + (边框上边距 + 边框下边距 + 2 * 内外框距离)
    bg_height = (line_height * lines) - text_config['line_space'] + (2 * text_config['margin']) + (
            bg_config['box_top_margin'] + bg_config['box_bottom_margin'] + (2 * bg_config['box_interval']))
    # 画布宽度 = 最长一行的宽度 + 2 * 正文侧面边距 + 2 * (边框侧面边距 + 内外框距离)
    bg_width = longest_line_width + (2 * text_config['side_margin']) + (
            2 * (bg_config['box_side_margin'] + bg_config['box_interval']))
    # 根据所有行的总高度及最长一行的宽度生成画布的大小
    bg_size = np.zeros((bg_height, bg_width, 4), dtype=np.uint8)
    canvas = Image.fromarray(bg_size)  # 生成绘图画布
    draw = ImageDraw.Draw(canvas)
    # 从这里开始绘图均为(x, y)坐标，横坐标x，纵坐标y
    # rectangle(起点坐标, 终点坐标) 绘制矩形，且方向必须为从左上到右下
    # 绘制一个与画布等大的矩形作为背景
    draw.rectangle(((0, 0), (bg_width, bg_height)), bg_config['background_color'], width=0)

    # 绘制外框
    # 外框左上点坐标 x=边框侧边距 y=边框上边距
    # 外框右下点坐标 x=画布宽度-边框侧边距 y=画布高度-边框上边距
    draw.rectangle(
        (
            (bg_config['box_side_margin'], bg_config['box_top_margin']),
            (bg_width - bg_config['box_side_margin'], bg_height - bg_config['box_bottom_margin'])
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])
    # 绘制内框
    # 内框左上点坐标 x=边框侧边距+内外框距离 y=边框上边距+内外框距离
    # 内框右下点坐标 x=画布宽度-边框侧边距-内外框距离 y=画布高度-边框上边距-内外框距离
    draw.rectangle(
        (
            (bg_config['box_side_margin'] + bg_config['box_interval'],
             bg_config['box_top_margin'] + bg_config['box_interval']),
            (bg_width - bg_config['box_side_margin'] - bg_config['box_interval'],
             bg_height - bg_config['box_bottom_margin'] - bg_config['box_interval'])
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])
    # 绘制左上小方形
    # 左上点坐标 x=边框侧边距-边长-边框厚度-1 y=边框上边距-边长-边框厚度-1 (1用于补偿PIL绘图的错位)
    # 右下点坐标 x=边框侧边距+边长-边框厚度-1 y=边框上边距+边长-边框厚度-1
    draw.rectangle(
        (
            (bg_config['box_side_margin'] - bg_config['wrap_width'] - bg_config['outline_width'] - 1,
             bg_config['box_top_margin'] - bg_config['wrap_width'] - bg_config['outline_width'] - 1),
            (bg_config['box_side_margin'] + bg_config['wrap_width'] - bg_config['outline_width'] - 1,
             bg_config['box_top_margin'] + bg_config['wrap_width'] - bg_config['outline_width'] - 1)
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])
    # 绘制右上小方形
    # 左上点坐标 x=画布宽度-边框侧边距-边框厚度+1 y=边框上边距-边长-边框厚度-1 (1用于补偿PIL绘图的错位)
    # 右下点坐标 x=画布宽度-边框侧边距+边长+边框厚度+1 y=边框上边距+边长-边框厚度-1
    draw.rectangle(
        (
            (bg_width - bg_config['box_side_margin'] - bg_config['outline_width'] + 1,
             bg_config['box_top_margin'] - bg_config['wrap_width'] - bg_config['outline_width'] - 1),
            (bg_width - bg_config['box_side_margin'] + bg_config['wrap_width'] + bg_config['outline_width'] + 1,
             bg_config['box_top_margin'] + bg_config['wrap_width'] - bg_config['outline_width'] - 1)
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])
    # 绘制左下小方形
    # 左上点坐标 x=边框侧边距-边长-边框厚度-1 y=画布高度-边框下边距-边框厚度+1 (1用于补偿PIL绘图的错位)
    # 右下点坐标 x=边框侧边距+边长-边框厚度-1 y=画布高度-边框下边距+边长+边框厚度+1
    draw.rectangle(
        (
            (bg_config['box_side_margin'] - bg_config['wrap_width'] - bg_config['outline_width'] - 1,
             bg_height - bg_config['box_bottom_margin'] - bg_config['outline_width'] + 1),
            (bg_config['box_side_margin'] + bg_config['wrap_width'] - bg_config['outline_width'] - 1,
             bg_height - bg_config['box_bottom_margin'] + bg_config['wrap_width'] + bg_config['outline_width'] + 1)
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])
    # 绘制右下小方形
    # 左上点坐标 x=画布宽度-边框侧边距-边框厚度+1 y=画布高度-边框下边距-边框厚度+1 (1用于补偿PIL绘图的错位)
    # 右下点坐标 x=画布宽度-边框侧边距+边长+边框厚度+1 y=画布高度-边框下边距+边长+边框厚度+1
    draw.rectangle(
        (
            (bg_width - bg_config['box_side_margin'] - bg_config['outline_width'] + 1,
             bg_height - bg_config['box_bottom_margin'] - bg_config['outline_width'] + 1),
            (bg_width - bg_config['box_side_margin'] + bg_config['wrap_width'] + bg_config['outline_width'] + 1,
             bg_height - bg_config['box_bottom_margin'] + bg_config['wrap_width'] + bg_config['outline_width'] + 1)
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])

    # 绘制正文文字
    # 开始坐标 x=边框侧边距+内外框距离+正文侧边距 y=边框上边距+内外框距离+正文上边距+行号*(行高+行距)
    for _ in range(len(text_list)):
        draw.text(
            (
                bg_config['box_side_margin'] + bg_config['box_interval'] + text_config['side_margin'],
                bg_config['box_top_margin'] + bg_config['box_interval'] + text_config['margin'] + (_ * line_height)
            ), text_list[_], fill=text_config['font_color'], font=font)

    # 绘制第一行额外文字
    # 开始坐标 x=边框侧边距+(4*内外框距离) y=画布高度-边框下边距+(2*内外框距离)
    draw.text(
        (
            bg_config['box_side_margin'] + (4 * bg_config['box_interval']),
            bg_height - bg_config['box_bottom_margin'] + (2 * bg_config['box_interval'])
        ), extra_text1, fill='#b4a08e', font=extra_font)
    # 绘制第二行额外文字
    # 开始坐标 x=边框侧边距+(4*内外框距离) y=画布高度-边框下边距+(3*内外框距离)+第一行额外文字的高度
    draw.text(
        (
            bg_config['box_side_margin'] + (4 * bg_config['box_interval']),
            bg_height - bg_config['box_bottom_margin'] + (3 * bg_config['box_interval']) +
            extra_font.getsize(extra_text1)[1]
        ), extra_text2, fill='#b4a08e', font=extra_font)

    canvas = canvas.convert(mode='RGB')  # 将RGBA转换为RGB以便保存为jpg
    # canvas.show()  # 展示生成结果
    temp_dir_path = os.path.join(os.path.dirname(__file__), 'temp')
    if not os.path.exists(temp_dir_path):  # 判断temp文件/文件夹是否存在
        os.mkdir(temp_dir_path)  # 不存在则创建temp文件夹
    elif os.path.isfile(temp_dir_path):  # 存在则判断temp是否为文件
        os.remove(temp_dir_path)  # 是文件则删掉后重新创建temp文件夹
        os.mkdir(temp_dir_path)
    img_name = 'temp_{}.jpg'.format(__get_time(2))  # 自定义临时文件的保存名称
    img_path = os.path.join(temp_dir_path, img_name)  # 自定义临时文件保存路径
    # 保存为图片 https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html?highlight=subsampling#jpeg
    canvas.save(img_path, format='JPEG', quality=95, optimize=True, progressive=True, subsampling=1, qtables='web_high')
    logger.debug(f'已生成图片并保存至: ↓\n{img_path}')
    return img_path


if __name__ == "__main__":
    pass

__all__ = [
    generate_img
]
