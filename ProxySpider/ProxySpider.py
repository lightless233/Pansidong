#!/usr/bin/env python
# coding: utf-8
import sys

from utils.AutoLoad import AutoLoad
from utils.ThreadPool import ThreadPool
from utils.data.LoggerHelp import logger
from utils.data.SaveData import SaveData

__author__ = "lightless"
__email__ = "root@lightless.me"

reload(sys)
sys.setdefaultencoding("utf-8")


class ProxySpider(object):
    def __init__(self, output_file=True, output_db=True, output_filename="proxy-ip-list.csv"):
        # 初始化AutoLoad模块
        self.al = AutoLoad()
        # 初始化
        self.tp = None
        self.sd = None
        self.write_file_tp = None
        self.spider_threads = None
        self.save_data_threads = None
        # 获取参数
        self.output_file = output_file
        self.output_db = output_db
        self.output_filename = output_filename

    def load(self, *spiders):
        self.al.load(*spiders)

    def set_threads(self, spider_threads=0, save_data_threads=0):
        if spider_threads > 0:
            self.spider_threads = spider_threads
        if save_data_threads > 0:
            self.save_data_threads = save_data_threads

    def start(self):
        if not len(self.al.spiders):
            logger.error("No Spiders loaded. exit.")
            sys.exit(1)
        else:
            message = "Loaded spiders: "
            for s in self.al.spiders:
                message += str(s.__class__).split(".")[-1].split("'")[0] + ", "
            logger.info(message.strip(", "))
        # 创建线程池
        if self.spider_threads:
            self.tp = ThreadPool(self.spider_threads)
        else:
            self.tp = ThreadPool()
        for sp in self.al.spiders:
            # 将spider中的run方法添加到线程池中
            self.tp.add_function(sp.run)
        # 开始线程池
        self.tp.run(join=False)

        # 输出结果
        self.sd = SaveData(self.al.results, self.tp, use_file=self.output_file, use_database=self.output_db,
                           filename=self.output_filename)
        if self.save_data_threads:
            self.write_file_tp = ThreadPool(self.save_data_threads)
        else:
            self.write_file_tp = ThreadPool()
        self.write_file_tp = ThreadPool()
        self.write_file_tp.add_function(self.sd.write)
        self.write_file_tp.run()


if __name__ == "__main__":
    ps = ProxySpider()
    ps.load()
    ps.start()
