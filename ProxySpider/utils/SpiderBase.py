#!/usr/bin/env python
# coding: utf-8
import os
import sys
import platform


__author__ = "lightless"
__email__ = "root@lightless.me"


class SpiderBase(object):
    def __init__(self):
        self.result_queue = None
        self.phantomjs_path = None

    def set_result_queue(self, result_queue):
        self.result_queue = result_queue

    def set_phantomjs_path(self):
        if "Windows" in platform.system():
            self.phantomjs_path = os.getcwd() + os.sep + "phantomjs" + os.sep + "phantomjs.exe"
        elif "Linux" in platform.system():
            self.phantomjs_path = os.getcwd() + os.sep + "phantomjs" + os.sep + "phantomjs"
        else:
            print "Unsupported operating system."
            sys.exit(1)

