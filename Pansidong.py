#!/usr/bin/env python2
# coding: utf-8
# file: Pansidong.py
# time: 2016/8/5 23:48

from utils.ArgParser import ParseCommandArgs

__author__ = "lightless"
__email__ = "root@lightless.me"


"""
项目入口文件
"""


def main():
    parse = ParseCommandArgs.ParseCommandArgs()
    parse.start_parse()


if __name__ == '__main__':
    main()







