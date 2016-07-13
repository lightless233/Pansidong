#!/usr/bin/env python
# coding: utf-8

import ConfigParser

import requests
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.data.LoggerHelp import logger
from utils.data.Tables import Proxy

__author__ = "lightless"
__email__ = "root@lightless.me"


class ProxyManage(object):
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read("config.ini")
        db_name = cf.get("ProxySpider", "database")
        username = cf.get(db_name, "username")
        password = cf.get(db_name, "password")
        host = cf.get(db_name, "host")
        database = cf.get(db_name, "database")

        self.engine = create_engine("mysql://" + username + ":" + password + "@" + host + "/" + database)
        self.db_session = sessionmaker(bind=self.engine)
        self.session = self.db_session()

        self.headers = {'User-Agent': 'curl/7.49.1'}

    def check(self):
        """
        Check if the proxy address is valid.
        :return: None
        """
        proxy_list = self.session.query(Proxy).filter(Proxy.id <= 10).all()
        for proxy in proxy_list:
            proxy_ip = proxy.ip
            proxy_port = proxy.port
            logger.info("Testing %s:%s" % (proxy_ip, proxy_port))
            r = self.__check_proxy(proxy_ip, proxy_port)
            logger.debug("Time: " + str(r.get("time")) + " Success: " + str(r.get("success")))

    def __check_proxy(self, proxy_ip, proxy_port):
        retry = 3
        time_summary = 0.0
        success_count = 0
        while retry:
            logger.debug("Retrying left: %d" % retry)
            proxies = {
                'http': proxy_ip + ":" + proxy_port
            }
            time_start = time.time()
            try:
                requests.get("http://ip.cn", headers=self.headers, proxies=proxies, timeout=20)
                elapsed_time = time.time() - time_start
                time_summary += elapsed_time
                success_count += 1
            except requests.RequestException, e:
                logger.debug(e.message)
                continue
            finally:
                retry -= 1
        ret_val = dict()
        ret_val['success'] = success_count
        ret_val['time'] = 0 if success_count == 0 else "%.2f" % (time_summary/success_count)
        return ret_val





