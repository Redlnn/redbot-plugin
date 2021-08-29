#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .config import read_cfg
from .info import MODULE_NAME

__all__ = [
    "generate_img"
]

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

cfg = read_cfg()


def _get_text_config() -> dict:
    """
    获取正文配置
    """
    font_name: str = cfg['text_to_img']['text_config']['font_name']
    ttf_path: str = os.path.join(os.getcwd(), 'plugins', 'fonts', font_name)  # 字体文件的路径
    if not os.path.exists(ttf_path):
        raise ValueError(f'文本转图片所用的字体文件不存在，请检查配置文件，尝试访问的路径如下：↓\n{ttf_path}')
    if len(font_name) < 6 or font_name[-4:] not in ('.ttf', '.ttc', '.otf', '.otc'):
        raise ValueError('所配置的字体文件名不正确，请检查配置文件')
    is_ttc_font: bool = True if font_name.endswith('.ttc') or font_name.endswith('.otc') else False
    ttc_font_index: int = cfg['text_to_img']['text_config']['ttc_font_index']  # ttc/otc的字形索引号
    font_size: int = cfg['text_to_img']['text_config']['font_size']  # 字体大小
    font_color: str = cfg['text_to_img']['text_config']['font_color']  # 字体颜色
    line_space: int = cfg['text_to_img']['text_config']['line_space']  # 行间距
    margin: int = cfg['text_to_img']['text_config']['margin']  # 上下左右距离内框的间距
    char_per_line: int = cfg['text_to_img']['text_config']['char_per_line']
    text_config = {
        'ttf_path': ttf_path,
        'is_ttc_font': is_ttc_font,
        'ttc_font_index': ttc_font_index,
        'font_size': font_size,
        'font_color': font_color,
        'line_space': line_space,
        'margin': margin,
        'char_per_line': char_per_line
    }
    # text_config = {
    #     'ttf_path': r'C:\Windows\Fonts\OPPOSans-B.ttf',
    #     'is_ttc_font': False,
    #     'ttc_font_index': 1,
    #     'font_size': 50,
    #     'font_color': '#645647',
    #     'line_space': 30,
    #     'margin': 80,
    #     'char_per_line': 25
    # }
    return text_config


def _get_background_config() -> dict:
    """
    获取背景配置
    """
    background_color: str = cfg['text_to_img']['background_config']['background_color']  # 背景颜色
    box_side_margin: int = cfg['text_to_img']['background_config']['box_side_margin']  # 外框距左右边界距离
    box_top_margin: int = cfg['text_to_img']['background_config']['box_top_margin']  # 外框距上边界距离
    box_bottom_margin: int = cfg['text_to_img']['background_config']['box_bottom_margin']  # 外框距下边界距离
    box_interval: int = cfg['text_to_img']['background_config']['box_interval']  # 内外框距离
    wrap_width: int = cfg['text_to_img']['background_config']['wrap_width']  # 小正方形边长
    outline_width: int = cfg['text_to_img']['background_config']['outline_width']  # 边框内描边厚度
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
    #     'box_interval': 5,
    #     'wrap_width': 5,
    #     'outline_width': 5,  # 内描边
    #     'outline_color': '#e9e5d9'
    # }
    return background_config


def _get_time(mode: int = 1) -> str:
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


def _conver_line_to_list(text: str, char_per_line: int, line_width: int, font: ImageFont.FreeTypeFont, font_size):
    i = 0
    j = 0
    text_list = []
    # re_ = '[a-zA-Z0-9]'
    start_symbol = ('[', '{', '<', '(', '【', '《', '（', '〈', '〖', '［', '〔', '“', '‘', '『', '「', '〝')
    end_symbol = (',', '.', '!', '?', ';', ':', ']', '}', '>', ')', '%', '~', '…', '，', '。', '！,', '？', '；', '：', '】', '》', '）', '〉', '〗', '］', '〕', '”', '’', '～', '』', '」', '〞')
    while True:
        tmp_text = text[i:i + char_per_line + j]
        size = font.getsize(tmp_text)
        if abs(size[0] - line_width) < font_size:
            if i + char_per_line + j < len(text):
                if text[i + char_per_line + j] in end_symbol:
                    j += 1
                    text_list.append(text[i:i + char_per_line + j])
                elif text[i + char_per_line + j] in start_symbol:
                    j -= 1
                    text_list.append(text[i:i + char_per_line + j])
                elif text[i + char_per_line + j] == ' ':
                    text_list.append(tmp_text)
                    j += 1
                else:
                    text_list.append(tmp_text)
            else:
                text_list.append(tmp_text)
            i += char_per_line + j
            j = 0
        elif char_per_line + j > len(tmp_text):
            text_list.append(tmp_text)
            i += char_per_line + j
            j = 0
            break
        elif size[0] > line_width:
            j -= 1
            continue
        elif size[0] < line_width:
            j += 1
            continue
        if i >= len(text):
            break
    del tmp_text
    return text_list


def _conver_text_to_list(text: str, char_per_line: int, line_width: int, font: ImageFont.FreeTypeFont, font_size):
    text_list = text.splitlines(False)
    n_text_list = []
    for _ in text_list:
        if _ == '':
            n_text_list.append('')
        else:
            n_text_list.extend(_conver_line_to_list(_, char_per_line, line_width, font, font_size))
    return n_text_list


def generate_img(text: str = None) -> str:
    """
    根据输入的文本，生成一张图并返回图片文件的路径

    :param text: 文本
    :return: 图片文件的路径
    """
    text_config = _get_text_config()
    bg_config = _get_background_config()
    if text_config['is_ttc_font']:
        font = ImageFont.truetype(text_config['ttf_path'], size=text_config['font_size'],
                                  index=text_config['ttc_font_index'])  # 确定正文用的ttf字体
        extra_font = ImageFont.truetype(text_config['ttf_path'],
                                        size=text_config['font_size'] - int(0.3 * text_config['font_size']),
                                        index=text_config['ttc_font_index'])  # 确定而额外文本用的ttf字体
    else:
        # 确定正文用的ttf字体
        font = ImageFont.truetype(text_config['ttf_path'], size=text_config['font_size'])
        # 确定而额外文本用的ttf字体
        extra_font = ImageFont.truetype(text_config['ttf_path'],
                                        size=text_config['font_size'] - int(0.3 * text_config['font_size']))
    extra_text1 = '由 Red_lnn 的 Bot 生成'  # 额外文本1
    extra_text2 = _get_time()  # 额外文本2

    font_size = font.getsize('一')  # 一个字符框的大小
    line_height = font_size[1]  # 行高
    line_height += text_config['line_space']  # 加入行距
    line_width = text_config['char_per_line'] * font_size[0]  # 行宽

    text_list = _conver_text_to_list(text, text_config['char_per_line'], line_width, font, text_config['font_size'])
    lines = len(text_list)

    # 画布高度=((行高+行距)*行数)-行距+(2*正文边距)+(边框上边距+4*边框厚度+2*内外框距离+边框下边距)
    bg_height = (line_height * lines) - text_config['line_space'] + (2 * text_config['margin']) + (
            bg_config['box_top_margin'] + (4 * bg_config['outline_width']) + (2 * bg_config['box_interval'])
    ) + bg_config['box_bottom_margin']
    # 画布宽度=行宽+2*正文侧面边距+2*(边框侧面边距+(2*边框厚度)+内外框距离)
    bg_width = line_width + (2 * text_config['margin']) + (2 * (bg_config['box_side_margin'] + (
            2 * bg_config['outline_width']) + bg_config['box_interval']))
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
    # 内框左上点坐标 x=边框侧边距+外边框厚度+内外框距离 y=边框上边距+外边框厚度+内外框距离
    # 内框右下点坐标 x=画布宽度-边框侧边距-外边框厚度-内外框距离 y=画布高度-边框上边距-外边框厚度-内外框距离
    draw.rectangle(
        (
            (bg_config['box_side_margin'] + bg_config['outline_width'] + bg_config['box_interval'],
             bg_config['box_top_margin'] + bg_config['outline_width'] + bg_config['box_interval']),
            (bg_width - bg_config['box_side_margin'] - bg_config['outline_width'] - bg_config['box_interval'],
             bg_height - bg_config['box_bottom_margin'] - bg_config['outline_width'] - bg_config['box_interval'])
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])

    pil_compensation = bg_config['outline_width']-1 if bg_config['outline_width'] > 1 else 0

    # 绘制左上小方形
    # 左上点坐标 x=边框侧边距-边长-2*边框厚度+补偿 y=边框侧边距-边长-2*边框厚度+补偿 (补偿PIL绘图的错位)
    # 右下点坐标 x=边框侧边距+补偿 y=边框上边距+补偿
    draw.rectangle(
        (
            (bg_config['box_side_margin'] - bg_config['wrap_width'] - (2 * bg_config['outline_width']) + pil_compensation,  # noqa
             bg_config['box_top_margin'] - bg_config['wrap_width'] - (2 * bg_config['outline_width']) + pil_compensation),  # noqa
            (bg_config['box_side_margin'] + pil_compensation,
             bg_config['box_top_margin'] + pil_compensation)
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])
    # 绘制右上小方形
    # 左上点坐标 x=画布宽度-(边框侧边距+补偿) y=边框侧边距-边长-2*边框厚度+补偿 (补偿PIL绘图的错位)
    # 右下点坐标 x=画布宽度-(边框侧边距-边长-2*边框厚度+补偿) y=边框上边距+补偿
    draw.rectangle(
        (
            (bg_width - bg_config['box_side_margin'] - pil_compensation,
             bg_config['box_top_margin'] - bg_config['wrap_width'] - (2 * bg_config['outline_width']) + pil_compensation),  # noqa
            (bg_width - bg_config['box_side_margin'] + bg_config['wrap_width'] + (2 * bg_config['outline_width'] - pil_compensation),  # noqa
             bg_config['box_top_margin'] + pil_compensation)
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])
    # 绘制左下小方形
    # 左上点坐标 x=边框侧边距-边长-2*边框厚度+补偿 y=画布高度-(边框下边距+补偿) (补偿PIL绘图的错位)
    # 右下点坐标 x=边框侧边距+补偿 y=画布高度-(边框侧边距-边长-2*边框厚度+补偿)
    draw.rectangle(
        (
            (bg_config['box_side_margin'] - bg_config['wrap_width'] - (2 * bg_config['outline_width']) + pil_compensation,  # noqa
             bg_height - bg_config['box_bottom_margin'] - pil_compensation),
            (bg_config['box_side_margin'] + pil_compensation,
             bg_height - bg_config['box_bottom_margin'] + bg_config['wrap_width'] + (2 * bg_config['outline_width']) - pil_compensation)  # noqa
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])
    # 绘制右下小方形
    # 左上点坐标 x=画布宽度-(边框侧边距+补偿) y=画布高度-(边框下边距+补偿) (补偿PIL绘图的错位)
    # 右下点坐标 x=画布宽度-(边框侧边距-边长-2*边框厚度+补偿) y=画布高度-(边框侧边距-边长-2*边框厚度+补偿)
    draw.rectangle(
        (
            (bg_width - bg_config['box_side_margin'] - pil_compensation,
             bg_height - bg_config['box_bottom_margin'] - pil_compensation),
            (bg_width - bg_config['box_side_margin'] + bg_config['wrap_width'] + (2 * bg_config['outline_width'] - pil_compensation),  # noqa
             bg_height - bg_config['box_bottom_margin'] + bg_config['wrap_width'] + (2 * bg_config['outline_width']) - pil_compensation)  # noqa
        ), fill=None, outline=bg_config['outline_color'], width=bg_config['outline_width'])

    # 绘制正文文字
    # 开始坐标 x=边框侧边距+2*边框厚度+内外框距离+正文侧边距 y=边框上边距+2*边框厚度+内外框距离+正文上边距+行号*(行高+行距)
    for _ in range(lines):
        draw.text(
            (
                bg_config['box_side_margin'] + (2 * bg_config['outline_width']) + bg_config['box_interval'] + text_config['margin'],  # noqa
                bg_config['box_top_margin'] + (2 * bg_config['outline_width']) + bg_config['box_interval'] + text_config['margin'] + (_ * line_height)  # noqa
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
    img_name = 'temp_{}.jpg'.format(_get_time(2))  # 自定义临时文件的保存名称
    img_path = os.path.join(temp_dir_path, img_name)  # 自定义临时文件保存路径
    # 保存为图片 https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html?highlight=subsampling#jpeg
    canvas.save(img_path, format='JPEG', quality=95, optimize=True, progressive=True, subsampling=1, qtables='web_high')
    # img_name = 'temp_{}.png'.format(__get_time(2))  # 自定义临时文件的保存名称
    # img_path = os.path.join(temp_dir_path, img_name)  # 自定义临时文件保存路径
    # # 保存为图片 https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html?highlight=subsampling#png
    # canvas.save(img_path, format='PNG', optimize=True)
    logger.debug(f'已生成图片并保存至: ↓\n{img_path}')
    return img_path


if __name__ == "__main__":
    pass
