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

normal:  # 此项下的内容会回复纯文本，本项实时生效
  此处填关键词: 此处填要回复的内容

with_img:  # 此项下的内容会生成图片来回复，本项实时生效
  此处填关键词1: 此处填要回复的内容
  此处填关键词2: |-
    此处填要回复的内容
    多行这样写噢，注意前面的空格
    实在不行用换行符也行

text_to_img:  # 此项为文字生成图片相关
  font_name: OPPOSans.ttf  # 字体文件的文件名（带后缀名），支持ttf/otf/ttc/otc
  font_size: 30  # 字体大小
  font_color: '#0E0E0E'  # 字体颜色，示例【#000000】
  line_space: 10  # 行间距
  left_margin: 60  # 左间距
  right_margin: 60  # 右间距
  top_margin: 90  # 上间距
  bottom_margin: 90  # 下间距
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
