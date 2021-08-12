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


def __get_font_config():
    """
    获取字体配置

    :return: ttf_path, font_size, font_color, line_space, left_margin, right_margin, top_margin, bottom_margin
    """
    ttf_path: str = os.path.join(os.getcwd(), 'plugins', 'fonts', cfg['text_to_img']['font_name'])  # 字体文件的路径
    if not os.path.exists(ttf_path):
        raise ValueError(f'文本转图片所用的字体文件不存在，尝试访问的路径如下：↓\n{ttf_path}')
    font_size: int = cfg['text_to_img']['font_size']  # 字体大小
    font_color: str = cfg['text_to_img']['font_color']  # 字体颜色
    line_space: int = cfg['text_to_img']['line_space']  # 行间距
    left_margin: int = cfg['text_to_img']['left_margin']  # 左间距
    right_margin: int = cfg['text_to_img']['right_margin']  # 右间距
    top_margin: int = cfg['text_to_img']['top_margin']  # 上间距
    bottom_margin: int = cfg['text_to_img']['bottom_margin']  # 下间距
    return ttf_path, font_size, font_color, line_space, left_margin, right_margin, top_margin, bottom_margin


def __get_time(mode: int) -> str:
    """
    :return: 返回当前时间，格式1970-01-01 12:00:00
    """
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    if mode == 1:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    elif mode == 2:
        dt = time.strftime("%Y-%m-%d_%H-%M-%S", time_local)
    else:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt


def __is_cjk_char(char: str):
    return True if regex.match(r'[\u2100-\u2BFF\u2E80-\u9FFF\uF900-\uFAFF\uFE30-\uFE4F\uFF01-\uFF64\uFFE0-\uFFE7]',
                               char) else False


def __cut_str2list(text, cut_len: int):
    if text == '':
        return ['']
    cut_result_list = []
    ansii_len = 0
    temp_str = ''
    for _ in text:
        if __is_cjk_char(_):
            ansii_len += 2
        else:
            ansii_len += 1
        temp_str += _
        if ansii_len < (cut_len * 2):
            continue
        cut_result_list.append(temp_str)
        temp_str = ''
        ansii_len = 0
    if temp_str != '':
        cut_result_list.append(temp_str)
    temp_str = ''
    ansii_len = 0
    return cut_result_list


# def __cut_str(text: str, cut_len: int):
#     temp_str = ''
#     for _ in text.split('\n'):
#         for __ in __cut_str2list(_, cut_len):
#             temp_str += f'{__}\n'
#     return temp_str


def __ansii_len(text: str):  # 非Ascii字符按两个字符算
    len_txt = len(text)
    len_txt_utf8 = len(text.encode('utf-8'))
    return int((len_txt_utf8 - len_txt) / 2 + len_txt)


# def __cut(obj, cut_len: int):
#     return [obj[i:i+cut_len] for i in range(0, len(obj), cut_len)] if obj != '' else ['']


def generate_img(text: str) -> str:
    """
    根据输入的文本，生成一张图并返回图片文件的路径

    :param text: 文本
    :return: 图片文件的路径
    """
    text_list = []
    for _ in text.split('\n'):
        text_list.extend(__cut_str2list(_, 25))
    # text_list.extend([''])
    # text_list.extend([f'                   （生成于: {__get_time(1)}）'])
    lines = len(text_list)  # 获取行数
    longest_text = ''
    a = 0
    for _ in text_list:  # 获取最长的一行
        size = __ansii_len(_)
        if size > a:
            longest_text = _
            a = size
    ttf_path, font_size, font_color, line_space, left_margin, right_margin, top_margin, bottom_margin = __get_font_config()
    font = ImageFont.truetype(ttf_path, font_size)  # 确定生成图片用的ttf字体
    w, h = font.getsize(longest_text)  # 获取最长的那一行的宽高
    h += line_space  # 加入行距
    bg = np.zeros((h * lines + top_margin + bottom_margin, w + h + left_margin + right_margin, 4),
                  dtype=np.uint8)  # 根据所有行的总高度及最长一行的宽度生成画布的大小
    bg = Image.fromarray(bg)  # 生成绘图画布
    draw = ImageDraw.Draw(bg)
    draw.rectangle([(0, 0), (w + h + left_margin + right_margin, h * lines + top_margin + bottom_margin)],
                   (230, 230, 230))  # 绘制一个与画布等大的矩形作为背景
    for _ in range(len(text_list)):
        draw.text((h / 2 + left_margin, _ * h + top_margin), text_list[_], fill=font_color, font=font)  # 绘制每一行的内容
    bg = bg.convert(mode='RGB')  # 将RGBA转换为RGB以便保存为jpg
    # bg.show()  # 展示生成结果
    temp_dir_path = os.path.join(os.path.dirname(__file__), 'temp')
    if not os.path.exists(temp_dir_path):  # 判断temp文件夹是否存在
        os.mkdir(temp_dir_path)
    if os.path.isfile(temp_dir_path):
        os.remove(temp_dir_path)
        os.mkdir(temp_dir_path)
    img_name = 'temp_{}.jpg'.format(__get_time(2))  # 定义保存名称
    img_path = os.path.join(temp_dir_path, img_name)  # 定义保存路径
    bg.save(img_path, format='JPEG', quality=80, subsampling=0)  # 保存为图片
    logger.debug(f'已生成图片并保存至: ↓\n{img_path}')
    return img_path


if __name__ == "__main__":
    pass

__all__ = [
    generate_img
]
