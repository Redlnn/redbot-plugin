#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
import logging
import os
import random

import yaml as yml
from graia.application.entry import (GraiaMiraiApplication, Group, MessageChain, Member, Plain, Source, At)  # noqa

from miraibot import GetCore

MODULE_NAME = '人品测试'
MODULE_DESC = '每个QQ号每天可随机获得一个0-100的整数（人品值），在当天内该值不会改变'
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = ()

data_folder = os.path.join(os.path.dirname(__file__), 'data')


def del_outdated_data(date: str) -> None:
    for _ in os.listdir(data_folder):
        if _ != f'data_{date}.yml':
            os.remove(os.path.join(data_folder, _))


def read_data(date: str, qq: int) -> int:
    del_outdated_data(date)
    data_file_path = os.path.join(data_folder, f'data_{date}.yml')
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
    if os.path.isfile(data_folder):
        os.remove(data_folder)
        os.mkdir(data_folder)

    with open(data_file_path, 'a+', encoding='utf-8') as f:
        f.seek(0, 0)
        yml_data: dict = yml.safe_load(f)
        f.seek(0, 2)
        if yml_data is None:
            random_int = random.randint(0, 100)
            yml.dump({str(qq): random_int}, f, allow_unicode=True)
            return random_int
        if str(qq) in yml_data.keys():
            return yml_data[str(qq)]
        else:
            random_int = random.randint(0, 100)
            yml.dump({str(qq): random_int}, f, allow_unicode=True)
            return random_int


@bcc.receiver('GroupMessage')
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    if group.id not in active_group and active_group:
        return None

    if message.asDisplay().lower() in ('.jrrp', '!jrrp'):
        date_today = datetime.datetime.now().strftime('%Y-%m-%d')
        jrrp = read_data(date_today, member.id)

        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),
            Plain(f' 今天的人品值是: {jrrp}')
        ]), quote=message.get(Source).pop(0))  # noqa
