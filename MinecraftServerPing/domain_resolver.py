#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import traceback
import dns.resolver
from dns.rdatatype import RdataType
from dns.resolver import NoAnswer, NXDOMAIN

from .info import MODULE_NAME

__all__ = [
    "domain_resolver", "domain_resolver_srv"
]

logger = logging.getLogger(f'MiraiBot.{MODULE_NAME}')


def domain_resolver(domain: str):
    dns_resolver = dns.resolver.Resolver()
    dns_resolver.nameservers = ['119.29.29.29']
    try:
        resolve_result = dns_resolver.resolve(domain, 'A', tcp=True, lifetime=5)
    except:  # noqa
        logger.error(f'在解析【{domain}】的DNS记录时出错: ↓\n{traceback.format_exc()}')
        raise ValueError(f'在解析【{domain}】的DNS记录时出错')
    nameserver_answer = resolve_result.response.answer
    target_ip = nameserver_answer[0][0].address
    return target_ip


def domain_resolver_srv(domain: str):
    srv_domain = f'_minecraft._tcp.{domain}'
    dns_resolver = dns.resolver.Resolver()
    dns_resolver.nameservers = ['119.29.29.29']
    try:
        resolve_result = dns_resolver.resolve(srv_domain, 'SRV', tcp=True, lifetime=5)
    except (NoAnswer, NXDOMAIN):
        try:
            resolve_result = dns_resolver.resolve(domain, 'A', tcp=True, lifetime=5)
        except:  # noqa
            logger.error(f'在解析【{domain}】的DNS记录时出错: ↓\n{traceback.format_exc()}')
            raise ValueError(f'在解析【{domain}】的DNS记录时出错')
    except:  # noqa
        logger.error(f'在解析【{srv_domain}】的DNS记录时出错: ↓\n{traceback.format_exc()}')
        raise ValueError(f'在解析【{srv_domain}】的DNS记录时出错')
    nameserver_answer = resolve_result.response.answer
    if nameserver_answer[0][0].rdtype == RdataType.SRV:
        target_ip = str(nameserver_answer[0][0].target).rstrip('.')
        target_port = nameserver_answer[0][0].port
        return target_ip, target_port
    elif nameserver_answer[0][0].rdtype in (RdataType.A, RdataType.AAAA):
        target_ip = nameserver_answer[0][0].address
        return target_ip, None
