#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import traceback

from ruamel.yaml import YAML

from .info import MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

default_cfg = """\
active_group:  # 此项下为要生效的群组，清空即为所有群组都生效
# - 123456789
# - 012345678

text_to_img:  # 此项为文字生成图片相关
  text_config:  # 正文配置
    # 字体文件的文件名（带后缀名），支持ttf/otf/ttc/otc
    # 字体文件请放在插件目录的fonts文件夹内，即【plugins/fonts/*.ttf】
    font_name: OPPOSans.ttf
    # 若使用ttc/otc字体文件，则要加载的ttc/otc的字形索引号，不懂请填1
    # 具体索引号可安装afdko后使用 `otc2otf -r {name}.ttc`查看
    # afdko: https://github.com/adobe-type-tools/afdko
    ttc_font_index: 1
    font_size: 50  # 字体大小
    font_color: '#645647'  # 字体颜色
    line_space: 30  # 行间距
    margin: 80  # 上下左右距离内框的间距

  background_config:  # 背景设置
    background_color: '#fffcf6'  # 背景颜色
    box_side_margin: 50  # 外框距左右边界距离
    box_top_margin: 70  # 外框距上边界距离
    box_bottom_margin: 250  # 外框距下边界距离
    box_interval:  5  # 内外框距离
    wrap_width: 5  # 小正方形边长
    outline_width: 5  # 边框内描边厚度
    outline_color: '#e9e5d9'  # 边框颜色
"""

yaml = YAML()


def write_cfg() -> None:
    """
    写入新配置文件
    """
    with open(os.path.join(os.path.dirname(__file__), 'config.yml'), 'w', encoding='utf-8') as f:
        yaml.dump(yaml.load(default_cfg), f)
    logger.warning('缺少配置文件，已用缺省配置生成新配置文件')


def read_cfg():
    """
    读取配置文件

    :return: 包含配置信息的字典
    """
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'config.yml')):  # 文件不存在
        write_cfg()
    try:
        f = open(os.path.join(os.path.dirname(__file__), 'config.yml'), mode='r', encoding='utf-8')
        cfg_dict = yaml.load(f)
        f.close()
        logger.debug(f'配置文件内容: ↓\n{cfg_dict}')
        return cfg_dict
    except:  # noqa
        logger.error(f'打开配置文件时出现错误: ↓\n{traceback.format_exc()}')
        raise ValueError(f'打开配置文件时出现错误: ↓\n{traceback.format_exc()}')


if __name__ == '__main__':
    print(read_cfg()['active_group'])

__all__ = [read_cfg]
