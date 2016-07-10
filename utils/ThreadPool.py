#!/usr/bin/env python
# coding: utf-8

import Queue
import threading
from multiprocessing import cpu_count
import time

from utils.data.LoggerHelp import logger

__all__ = ["ThreadPool"]

__author__ = "lightless"
__email__ = "root@lightless.me"


class ThreadPool(object):
    def __init__(self, thread_count=cpu_count()*2):
        self.__thread_count = thread_count
        self.__function_list = Queue.Queue()
        self.__thread_list = []
        self.__alive_thread_counts = 0
        self.__working_thread_list = []
        self.__dead_threads = []
        self.finished = False

    def add_function_list(self, function_list=[]):
        for fn in function_list:
            self.add_function(fn[0], **fn[1])

    def add_function(self, func, **kwargs):
        if callable(func):
            self.__function_list.put((func, kwargs))

    def run(self, join=True):
        # 从队列中获取工作函数
        while not self.__function_list.empty():
            fn = self.__function_list.get_nowait()
            try:
                thread_name = str(fn[0].im_class).split(".")[-1].split("'")[0]
            except AttributeError:
                thread_name = fn[0].__name__
            t = threading.Thread(target=fn[0], name=thread_name, kwargs=fn[1])
            self.__thread_list.append(t)

        tt = threading.Thread(target=self._run, args=(join,), name="really_run")
        # tt.setDaemon(True)
        tt.start()
        # tt.join()

    def is_all_thread_dead(self):
        flags = True
        for t in self.__thread_list:
            if t.is_alive():
                flags = False
            elif t not in self.__dead_threads:
                    logger.debug("[*] " + t.getName() + " finished.")
                    self.__dead_threads.append(t)
        return flags

    def __get_current_alive_thread_count(self):
        alive_cnt = 0
        for t in self.__working_thread_list:
            if t.is_alive():
                alive_cnt += 1
        self.__alive_thread_counts = alive_cnt
        return alive_cnt

    def _run(self, join=True):
        for t in self.__thread_list:
            # 等待线程
            while True:
                if self.__get_current_alive_thread_count() < self.__thread_count:
                    break
                else:
                    time.sleep(0.5)
            # 获取到了空闲的位置，从工作列表中删除已经停止的线程
            for tt in self.__working_thread_list:
                if not tt.is_alive():
                    logger.debug("[*] " + tt.getName() + " deleted from working list.")
                    self.__working_thread_list.remove(tt)
            # 等待到了空闲的位置，将该任务添加到工作列表中
            self.__working_thread_list.append(t)
            # 开始线程
            logger.debug("[*] " + t.getName() + " start.")
            t.start()
            if join:
                for tt in self.__working_thread_list:
                    tt.join()
        while True:
            if self.is_all_thread_dead():
                self.finished = True
                break
            else:
                time.sleep(0.5)

    @staticmethod
    def get_all_threads():
        return threading.enumerate()
