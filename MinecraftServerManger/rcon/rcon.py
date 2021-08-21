#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import traceback

from mctools import RCONClient

from ..info import MODULE_NAME
from .config import read_cfg

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')
cfg = read_cfg()

__HOST = cfg['server']  # Hostname of the Minecraft server
__PORT = cfg['port']  # Port number of the RCON server
__PASSWORD = cfg['password']  # Password of the RCON server


def execute_command(command: str) -> tuple[None, str]:
    """

    通过 RCON 连接服务器
    可用于执行控制台指令

    :param command: 需要执行的命令
    :reurn: 执行命令返回值
    """
    logger.debug(f'将在{__HOST}:{__PORT}上执行【{command}】')
    rcon = RCONClient(host=__HOST, port=__PORT, format_method=2, timeout=6)
    try:
        rcon.login(__PASSWORD)
    except Exception as e:
        logger.error(f'RCON连接失败: ↓\n{traceback.format_exc()}')
        raise e
    resp: str = rcon.command(command)
    logger.debug(f'服务器返回值如下: ↓\n{resp}')
    if resp == '':
        return None
    else:
        return resp.rstrip()


__all__ = [
    execute_command
]
