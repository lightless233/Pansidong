#!/usr/bin/env python2
# coding: utf-8
# file: Pansidong.py
# time: 2016/8/5 23:48

import sys

from utils.ArgParser import ArgParse
from utils.ArgParser.Messages import Version
from utils.data.LoggerHelp import logger
from Cores.ProxySpider.ProxySpider import ProxySpider

__author__ = "lightless"
__email__ = "root@lightless.me"


"""
项目入口文件
"""


def main():

    command_args = ArgParse.pansidong_parse.parse_args()

    # --version
    if command_args.version:
        print Version
        sys.exit(0)

    # --update-proxy-db
    if command_args.update_proxy_db:
        logger.debug("Update Proxy DB selected.")
        ps = ProxySpider()
        ps.load()
        ps.start()
        sys.exit(0)


if __name__ == '__main__':
    main()







