#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import socket
import traceback

import regex
from mctools import PINGClient
from requests.exceptions import ConnectTimeout, ReadTimeout, Timeout
from urllib3.exceptions import TimeoutError

from .domain_resolver import domain_resolver, domain_resolver_srv
from .info import MODULE_NAME

__all__ = [
    "ping_client"
]

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')


def _is_domain(value: str) -> bool:
    """
    Return whether or not given value is a valid domain.
    If the value is valid domain name this function returns ``True``, otherwise False
    :param value: domain string to validate
    """
    pattern = regex.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )
    return True if pattern.match(value) else False


def _is_ip(host: str) -> bool:
    return True if regex.match(r'^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$',
                               host) else False


def _raw(text: bytes) -> str:
    """
    Return a raw string representation of text
    将包含字符串的 byte 流转换为普通字符串，同时删除其中的终端控制符号
    """
    trans_map = {
        '\x1b': r'\x1b',
    }
    new_str = ''
    for char in text:
        try:
            new_str += trans_map[char]  # noqa
        except KeyError:
            new_str += char
    return new_str


def ping_client(target: str):
    target = target.split(':')
    if len(target) > 2:
        return '参数错误，请检查你的输入'
    elif len(target) == 1:
        if _is_domain(target[0]):
            # 如果目标为域名，则有可能是A记录（默认25565）或SRV记录
            target_server, target_port = domain_resolver_srv(target[0])
            if target_port is None:  # A记录
                target_port = 25565
            else:  # SRV记录
                target_port = int(target_port)
        elif _is_ip(target[0]):
            target_server = target[0]
            target_port = 25565
        else:
            return f'【{target[0]}】不是合法的域名/IP地址'
    else:
        if not target[1].isdigit():
            return f'【{target[1]}】不是合法的端口号'
        if _is_domain(target[0]):
            target_server = domain_resolver(target[0])
        elif _is_ip(target[0]):
            target_server = target[0]
        else:
            return f'【{target[0]}】不是合法的域名/IP地址'
        target_port = target[1]

    try:
        ping = PINGClient(host=target_server, port=target_port, format_method=2, timeout=5)
        stats = ping.get_stats()
        ping.stop()
        motd = stats['description']
    except KeyError:
        ping = PINGClient(host=target_server, port=target_port, timeout=5)
        stats = ping.get_stats()
        ping.stop()
        motd = regex.sub(r'[\\]x1b[[]([0-9_;]*)m', '', _raw(stats['description']))
    except ConnectionRefusedError:
        error_text = f'在尝试ping【{target_server}:{target_port}】时出错: ' \
                     '连接被目标拒绝，该地址和端口可能不存在Minecraft服务器'
        logger.error(error_text + f' ↓\n{traceback.format_exc()}')
        return error_text
    except (Timeout, ReadTimeout, ConnectTimeout, TimeoutError, socket.timeout):
        error_text = f'在尝试ping【{target_server}:{target_port}】时连接超时'
        logger.error(error_text + f' ↓\n{traceback.format_exc()}')
        return error_text
    except Exception as e:  # noqa
        error_text = f'在尝试ping【{target_server}:{target_port}】时出现未知错误:'
        logger.error(error_text + f' ↓\n{traceback.format_exc()}')
        return error_text + str(e)

    version = str(stats['version']['name'])
    protocol = str(stats['version']['protocol'])
    delay = str(round(stats['time'], 1))
    online_player = str(stats['players']['online'])
    max_player = str(stats['players']['max'])

    if stats['players'].get('sample'):
        player_list: list = stats['players'].get('sample')
    else:
        player_list = []

    return {
        'version': version,
        'protocol': protocol,
        'motd': motd,
        'delay': delay,
        'online_player': online_player,
        'max_player': max_player,
        'player_list': player_list
    }
