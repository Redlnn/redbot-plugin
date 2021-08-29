#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import traceback

from ruamel.yaml import YAML

from ..info import MODULE_NAME

__all__ = [
    "read_cfg"
]

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

default_cfg = """\
database: minecraft
table: whitelist
mysql:
  enable: true
  host: 127.0.0.1
  port: 3306
  user: admin
  password: admin
"""

yaml = YAML()
config_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')


def write_cfg() -> None:
    """
    写入新配置文件
    """
    with open(os.path.join(config_folder, 'database.yml'), 'w', encoding='utf-8') as f:
        yaml.dump(yaml.load(default_cfg), f)
    logger.warning('缺少数据库配置文件，已用缺省配置生成新文件')


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
    elif not os.path.exists(os.path.join(config_folder, 'database.yml')):  # 文件不存在
        write_cfg()
    try:
        f = open(os.path.join(config_folder, 'database.yml'), mode='r', encoding='utf-8')
        cfg_dict = yaml.load(f)
        f.close()
        logger.debug(f'数据库配置文件内容: ↓\n{cfg_dict}')
        return cfg_dict
    except:  # noqa
        logger.error(f'打开数据库配置文件时出现错误: ↓\n{traceback.format_exc()}')
        raise ValueError(f'打开数据库配置文件时出现错误: ↓\n{traceback.format_exc()}')


if __name__ == '__main__':
    pass
