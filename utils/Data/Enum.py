#!/usr/bin/env python2
# coding: utf-8
# file: Enum.py
# time: 2016/8/6 15:19

__author__ = "lightless"
__email__ = "root@lightless.me"


class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
