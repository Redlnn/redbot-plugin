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
"""

yaml = YAML()
config_folder = os.path.join(os.path.dirname(__file__), 'config')


def write_cfg() -> None:
    """
    写入新配置文件
    """
    with open(os.path.join(config_folder, 'default.yml'), 'w', encoding='utf-8') as f:
        yaml.dump(yaml.load(default_cfg), f)
    logger.warning('缺少配置文件，已用缺省配置生成新配置文件')


def read_cfg():
    """
    读取配置文件

    :return: 包含配置信息的字典
    """
    if not os.path.exists(config_folder):
        os.mkdir(config_folder)
    elif os.path.isfile(config_folder):
        os.remove(config_folder)
        os.mkdir(config_folder)
    elif not os.path.exists(os.path.join(config_folder, 'default.yml')):  # 文件不存在
        write_cfg()
    try:
        f = open(os.path.join(config_folder, 'default.yml'), mode='r', encoding='utf-8')
        cfg_dict = yaml.load(f)
        f.close()
        logger.debug(f'配置文件内容: ↓\n{cfg_dict}')
        return cfg_dict
    except:  # noqa
        logger.error(f'打开配置文件时出现错误: ↓\n{traceback.format_exc()}')
        raise ValueError(f'打开配置文件时出现错误: ↓\n{traceback.format_exc()}')


if __name__ == '__main__':
    pass

__all__ = [read_cfg]
