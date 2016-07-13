#!/usr/bin/env python
# coding: utf-8
import os
import sys
import platform

from utils.data.LoggerHelp import logger


__author__ = "lightless"
__email__ = "root@lightless.me"


class SpiderBase(object):
    def __init__(self):
        self.result_queue = None
        self.phantomjs_path = None

    def set_result_queue(self, result_queue):
        self.result_queue = result_queue

    def set_phantomjs_path(self):
        phantomjs_path = os.getcwd() + os.sep + "ThirdParty" + os.sep + "phantomjs" + os.sep

        if "Windows" in platform.system():
            self.phantomjs_path = phantomjs_path + "phantomjs.exe"
        elif "Linux" in platform.system() and "x86_64" in platform.machine():
            self.phantomjs_path = phantomjs_path + "phantomjs"
        else:
            logger.error("Unsupported operating system.")
            logger.error("Only Windows and Linux x86_64 was supported.")
            sys.exit(1)

