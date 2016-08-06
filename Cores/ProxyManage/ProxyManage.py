#!/usr/bin/env python
# coding: utf-8

import sys
import datetime
import time

import requests
from sqlalchemy.exc import SQLAlchemyError

from utils.Data.LoggerHelp import logger
from utils.DBConnection import DBConnection
from utils.Data.Tables import Proxy

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

        # 初始化数据库连接
        db = DBConnection.DBConnection()
        db.connect()
        self.session = db.session

        if kwargs.get("all", None) is not None:
            # 检查数据库中的全部ip
            pass
        elif kwargs.get("ips", None) is not None:
            # 检查提供的IP
            self._check_ip_list(kwargs.get("ips"))

    def __del__(self):
        del self.session

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
            logger.debug("Times: {0}. Trying {1}:{2} connection...".format(2-retry+1, ip, port))
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

    def _check_ip_list(self, raw_ips):
        try:
            if raw_ips is not None and len(raw_ips):
                ips = raw_ips.split(",")
                for ip in ips:
                    ip_stu = ip.split(":")
                    s, t = self._check(ip_stu[0], ip_stu[1])
                    logger.info("IP {0} Connect {1}, time: {2:.2f}s".format(ip, "success", t)) if s \
                        else logger.error("IP {0} Connect failed.".format(ip))
                    self._update_db(ip_stu[0], ip_stu[1], t, s)
            else:
                logger.fatal("No IP provide.")
                sys.exit(1)
        except KeyError:
            logger.fatal("No IP provide.")
            sys.exit(1)

    def _update_db(self, ip, port, delay, alive):
        proxy_item = self.session.query(Proxy).filter(Proxy.ip == ip, Proxy.port == port).all()
        if len(proxy_item):
            # 数据库中已经有这个IP了，更新即可
            proxy_item = proxy_item[0]
            proxy_item.updated_time = datetime.datetime.now()
            proxy_item.times = delay
            proxy_item.is_alive = 1 if alive else 0
            try:
                self.session.add(proxy_item)
                self.session.commit()
            except SQLAlchemyError, e:
                logger.error("Error while update proxy information to database.")
                logger.error(e.message)
                sys.exit(1)
        elif not len(proxy_item):
            # 数据库中没有IP，添加进去
            new_proxy = Proxy(
                ip=ip, port=port, proxy_type=None, location=None, protocol=None, times=delay, is_alive=1,
                created_time=datetime.datetime.now(), updated_time=datetime.datetime.now()
            )
            try:
                self.session.add(new_proxy)
                self.session.commit()
            except SQLAlchemyError, e:
                logger.error("Error while update proxy information to database.")
                logger.error(e.message)
                sys.exit(1)

