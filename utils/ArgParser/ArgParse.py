#!/usr/bin/env python2
# coding: utf-8
# file: ArgParse.py
# time: 2016/8/6 10:45

import argparse

from utils.ArgParser.Messages import Banner

__author__ = "lightless"
__email__ = "root@lightless.me"
__all__ = ["pansidong_parse"]

# 初始化参数
pansidong_parse = argparse.ArgumentParser(description=Banner, formatter_class=argparse.RawTextHelpFormatter)

# 设置命令组
misc_group = pansidong_parse.add_argument_group("Misc")
proxy_group = pansidong_parse.add_argument_group("Proxy")
attack_group = pansidong_parse.add_argument_group("Attack")
spider_group = pansidong_parse.add_argument_group("Spider")

# 添加Misc组的命令
misc_group.add_argument("--version", help="Show program version.", action="store_true")

# 添加Proxy组的命令
proxy_group.add_argument("--update-proxy-db", help="Update proxy IP Address.", action="store_true")
proxy_group.add_argument("--check-proxy", metavar="IP:PORT", type=str, help="Check proxy availability.")
proxy_group.add_argument("--check-proxy-all", help="Check ALL proxy availability. !!VERY SLOW!!", action="store_true")
proxy_group.add_argument("--get-alive-proxy", help="Get all alive proxy from db. e.g. --get-alive-proxy 100, 2",
                         type=str, metavar="[count[, delay]]")
proxy_group.add_argument("--clean-db", help="Clean the dead proxy from db.", action="store_true")

# 添加Attack组的命令


# 添加spider组的命令
proxy_group.add_argument("--spider-only", help="Spider the target, do not scan.", metavar="URL", type=str)
