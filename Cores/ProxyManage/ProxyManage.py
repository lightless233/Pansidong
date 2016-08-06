#!/usr/bin/env python
# coding: utf-8

import sys
import ConfigParser
import datetime
import time

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.data.LoggerHelp import logger
from utils.data.Tables import Proxy

__author__ = "lightless"
__email__ = "root@lightless.me"


class ProxyManage(object):

    def __init__(self, **kwargs):
        """
        初始化代理地址检查
        :param kwargs:
                        all: True: 检测数据库中全部的IP, False：检测指定的IP列表，以逗号分隔
                        ips: 待检测的IP，"1.1.1.1:80, 2.2.2.2:3128"
        """
        super(ProxyManage, self).__init__()

        # request headers
        self.headers = {
            'User-Agent': 'curl/7.49.1',
        }

        if kwargs.get("all", None) is not None:
            # 检查数据库中的全部ip
            pass
        else:
            # 检查提供的IP
            try:
                raw_ips = kwargs.get("ips", None)
                if raw_ips is not None:
                    ips = raw_ips.split(",")
                    for ip in ips:
                        ip_stu = ip.split(":")
                        s, t = self._check(ip_stu[0], ip_stu[1])
                        logger.info("IP {0} Connect {1}, time: {2}".format(ip, "success", t)) if s \
                            else logger.error("IP {0} Connect failed.".format(ip))
                else:
                    logger.fatal("No IP provide.")
                    sys.exit(1)
            except KeyError:
                logger.fatal("No IP provide.")
                sys.exit(1)

    def _check(self, ip, port):

        # 检查参数合法性
        if ip == "" or port == "":
            logger.error("Invalid ip or port found. Skipping...")
            return False, -1.0

        # 2次重试机会
        retry = 2
        time_summary = 0.0
        success = False
        while retry:
            logger.debug("Trying {0}:{1} connection...".format(ip, port))
            proxies = {
                'http': ip + ":" + port
            }

            try:
                time_start = time.time()
                requests.get("http://ip.cn/", headers=self.headers, proxies=proxies, timeout=10)
                time_summary = time.time() - time_start
                success = True
                break
            except requests.RequestException, e:
                logger.warning(e.message)
                continue
            finally:
                retry -= 1

        return success, time_summary


