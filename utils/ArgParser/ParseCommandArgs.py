#!/usr/bin/env python2
# coding: utf-8
# file: ParseCommandArgs.py
# time: 2016/8/6 11:59

import sys
import time

from Cores.ProxySpider import ProxySpider
from Cores.ProxyManage import ProxyManage
from Cores.WebSpider import WebSpider
from utils.ArgParser import ArgParse
from utils.ArgParser.Messages import Version
from utils.Data.LoggerHelp import logger

__author__ = "lightless"
__email__ = "root@lightless.me"

__all__ = ["ParseCommandArgs"]


# TODO： 按照不同的分类，拆分这个类
class ParseCommandArgs(object):
    def __init__(self):
        super(ParseCommandArgs, self).__init__()
        self.pansidong_parse = ArgParse.pansidong_parse
        self.command_args = self.pansidong_parse.parse_args()

    def start_parse(self):
        # --version
        if self.command_args.version:
            print Version
            sys.exit(0)

        # --update-proxy-db
        if self.command_args.update_proxy_db:
            logger.debug("Update Proxy DB selected.")
            ps = ProxySpider.ProxySpider()
            ps.load()
            ps.start()
            sys.exit(0)

        # --check-proxy
        if self.command_args.check_proxy:
            logger.debug("Check proxy selected.")
            ips = self.command_args.check_proxy
            logger.debug(ips)
            pm = ProxyManage.ProxyManage(ips=ips)
            pm.check()
            sys.exit(0)

        # --check-proxy-all
        if self.command_args.check_proxy_all:
            logger.debug("Check all proxy selected.")
            pm = ProxyManage.ProxyManage(all=True)
            pm.check()
            sys.exit(0)

        # --get-alive-proxy
        if self.command_args.get_alive_proxy:
            logger.debug("Get alive proxy selected.")
            logger.debug(self.command_args.get_alive_proxy)
            pm = ProxyManage.ProxyManage()
            params = self.command_args.get_alive_proxy
            if "," in params:
                amount = params.split(",")[0].strip()
                delay = params.split(",")[1].strip()
                pm.get_alive_proxy(amount, delay)
            else:
                pm.get_alive_proxy(params.strip())

        # --clean-db
        if self.command_args.clean_db:
            logger.debug("Clean db selected.")
            pm = ProxyManage.ProxyManage()
            pm.clean_dead_proxy()

        # --spider-only
        if self.command_args.spider_only:
            logger.debug("Spider only selected.")
            target_url = self.command_args.spider_only
            web_spider = WebSpider.WebSpider(target=target_url, deep=1, limit_domain=[target_url], phantomjs_count=1)
            web_spider.start()
            logger.info("Spider finished, wait for all threads and thread pool exit.")
            time.sleep(5)
            logger.info("Task done. :)")

