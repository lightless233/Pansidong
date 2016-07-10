#!/usr/bin/env python
# coding: utf-8
import os
import Queue

__author__ = "lightless"
__email__ = "root@lightless.me"


class AutoLoad:

    def __init__(self):
        self.spiders = []
        self.results = Queue.Queue()

    @staticmethod
    def __check_filename(filename):
        if not filename.endswith(".py") or filename.startswith("_"):
            return False
        else:
            return True

    def load_spider(self, filename):
        spider_name = os.path.splitext(filename)[0]
        spider = __import__("spiders." + spider_name, fromlist=[spider_name])
        spider_class = spider.get_spider_class()
        o = spider_class()
        o.set_result_queue(self.results)
        o.set_phantomjs_path()
        self.spiders.append(o)

    def load(self, *cls):
        if not cls:
            for filename in os.listdir("spiders"):
                if self.__check_filename(filename):
                    self.load_spider(filename)
        else:
            for class_name in cls:
                filename = class_name + ".py"
                if self.__check_filename(filename) and os.path.exists("spiders" + os.sep + class_name + ".py"):
                    self.load_spider(filename)


