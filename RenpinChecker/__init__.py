#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
import logging
import os
import random

import yaml as yml
from graia.application.entry import (At, GraiaMiraiApplication, Group, Member, MessageChain, Plain, Source)

from miraibot import GetCore
from miraibot.command import group_command

MODULE_NAME = '人品测试'
MODULE_DESC = '每个QQ号每天可随机获得一个0-100的整数（人品值），在当天内该值不会改变，该值会存放于一yml文件中，每日删除过期文件'
MODULE_AUTHOR = 'Red_lnn'
MODULE_AUTHOR_CONTACT = 'https://github.com/Redlnn'

bcc = GetCore.bcc()
__plugin_name__ = __name__ = MODULE_NAME
__plugin_usage__ = MODULE_DESC

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')

# 生效的群组，若为空，即()，则在所有群组生效
# 格式为：active_group = (123456, 456789, 789012)
active_group = ()

data_folder = os.path.join(os.path.dirname(__file__), 'data')


def del_outdated_data(date: str) -> None:
    """
    删除过时的数据文件
    """
    for _ in os.listdir(data_folder):
        if _ != f'data_{date}.yml':
            os.remove(os.path.join(data_folder, _))


def read_data(date: str, qq: str) -> int:
    """
    在文件中读取指定QQ今日已生成过的随机数，若今日未生成，则新生成一个随机数并写入文件
    """
    del_outdated_data(date)
    data_file_path = os.path.join(data_folder, f'data_{date}.yml')
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)  # 如果同级目录不存在data文件夹，则新建一个
    if os.path.isfile(data_folder):
        os.remove(data_folder)
        os.mkdir(data_folder)  # 如果同级目录存在data文件，则删除该文件后新建一个同名文件夹

    with open(data_file_path, 'a+', encoding='utf-8') as f:  # 以 追加+读 的方式打开文件
        f.seek(0, 0)  # 将读写指针放在文件头部
        yml_data: dict = yml.safe_load(f)  # 读写
        f.seek(0, 2)  # 将读写指针放在文件尾部
        if yml_data is None:  # 若文件为空，则生成一随机数并写入到文件中，然后返回生成的随机数
            random_int = random.randint(0, 100)
            yml.dump({qq: random_int}, f, allow_unicode=True)
            return random_int
        if qq in yml_data.keys():  # 若文件中有指定QQ的数据则读取并返回
            return yml_data[qq]
        else:  # 若文件中没有指定QQ的数据，则生成一随机数并写入到文件中，然后返回生成的随机数
            random_int = random.randint(0, 100)
            yml.dump({qq: random_int}, f, allow_unicode=True)
            return random_int


@group_command('!jrrp', ['！jrrp', '.jrrp', '#jrrp'], '你今天的人品如何？', group=active_group)  # jrrp 即 JinRiRenPin
async def group_message_listener(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    date_today = datetime.datetime.now().strftime('%Y-%m-%d')  # 获得今日日期
    jrrp = read_data(date_today, str(member.id))

    await app.sendGroupMessage(group, MessageChain.create([
        At(member.id),
        Plain(f' 今天的人品值是: {jrrp}')
    ]), quote=message.get(Source).pop(0))  # noqa
