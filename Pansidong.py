#!/usr/bin/env python2
# coding: utf-8
# file: Pansidong.py
# time: 2016/8/5 23:48

import sys

from utils.ArgParser import ParseCommandArgs

__author__ = "lightless"
__email__ = "root@lightless.me"


"""
项目入口文件
"""


def main():
    parse = ParseCommandArgs.ParseCommandArgs()

    if len(sys.argv) == 1:
        parse.pansidong_parse.print_help()
        sys.exit(1)

    parse.start_parse()


if __name__ == '__main__':
    main()







