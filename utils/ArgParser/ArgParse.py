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
attack_group = pansidong_parse.add_argument_group("Attack")
spider_group = pansidong_parse.add_argument_group("Spider")

# 添加Misc组的命令
misc_group.add_argument("--version", help="Show program version.", action="store_true")
misc_group.add_argument("--update-proxy-db", help="Update proxy IP Address.", action="store_true")
misc_group.add_argument("--check-proxy", metavar="[127.0.0.1:9050]",
                        type=str,
                        help="Check proxy availability. If none IP provide, it will check proxy pool.(!!SLOW!!)")

# 添加Attack组的命令


# 添加spider组的命令

