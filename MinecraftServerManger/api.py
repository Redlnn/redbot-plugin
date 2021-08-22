#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union
import requests
import regex
import time

from functools import wraps
from graia.application.entry import MemberPerm


class PrefixCheck:
    def __init__(self, prefix: str = None):
        self.prefix = prefix

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if args[0] != self.prefix:
                return None
            else:
                return func(*args, **kwargs)
        return decorated


class LengthCheck:
    def __init__(self, length: int = None):
        self.length = length

    def __call__(self, func):
        @wraps(func)
        async def decorated(*args, **kwargs):
            if len(args) != self.length:
                return None
            else:
                return await func(*args, **kwargs)
        return decorated


def get_time() -> str:
    """
    :return: 当前时间，格式1970-01-01 12:00:00
    """
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt


def PermissionCheck(func):  # noqa
    @wraps(func)
    async def decorated(*args, **kwargs):
        if kwargs['member'].permission not in (MemberPerm.Administrator, MemberPerm.Owner):
            return '你没有权限执行此命令'
        else:
            return await func(*args, **kwargs)
    return decorated


def is_mc_id(mc_id: str) -> bool:
    """
    判断是否为合法的正版ID

    :param mc_id: 正版用户名（id）
    :return: `True`为是，`False`为否
    """
    return True if 1 <= len(mc_id) <= 16 and regex.match(r'^[0-9a-zA-Z_]+$', mc_id) else False


def is_uuid(uuid: str) -> Union[str, bool]:
    """
    判断是否为合法uuid

    > Mojang API 使用简化的uuid

    :param uuid: 输入一个uuid
    :return: 'Full_UUID' 指带横杠的完整uuid，'Simple_UUID' 指没有横杠的简化uuid
    """
    if regex.match(r'^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$', uuid):
        return 'Full_UUID'
    elif regex.match(r'^[0-9a-z]{32}$', uuid):
        return 'Simple_UUID'
    else:
        return False


def get_uuid(mc_id: str) -> tuple[tuple[str, str], tuple[int, None]]:
    """
    通过 id 从 Mojang 获取 uuid

    :param mc_id: 正版用户名（id）
    :return: 大小写正确的用户名：name, 该用户名对应的简化：uuid
    """
    url = f'https://api.mojang.com/users/profiles/minecraft/{mc_id}'
    try:
        res = requests.get(url, timeout=5)
    except Exception as e:
        raise e
    code = res.status_code
    if code == 200:
        mc_name: str = res.json()['name']
        uuid: str = res.json()['id']
        return mc_name, uuid
    # elif code == 204:
    #     raise UnknownIDError
    else:
        return code, None


def get_mc_id(uuid: str) -> Union[None, str, int]:
    """
    通过 uuid 从 Mojang 获取正版 id

    :param uuid: 输入一个uuid
    :return: 正版ID
    """
    if not is_uuid(uuid):
        return None
    url = f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}'
    try:
        res = requests.get(url, timeout=5)
    except Exception as e:
        raise e
    code = res.status_code
    if code == 200:
        return res.json()['name']
    # elif code == 204:
    #     raise UnknownUUIDError
    # elif code == 400:
    #     raise InvalidUUIDError
    else:
        raise code
