#!/usr/bin/env python2
# coding: utf-8
# file: ThreadPool4
# time: 2016/7/23 20:12

import Queue
from multiprocessing import cpu_count
import threading
import time
import os

from utils.Data.LoggerHelp import logger

__author__ = "lightless"
__email__ = "root@lightless.me"


class ThreadPool(object):
    def __init__(self, thread_count=cpu_count()):

        # 初始化相关变量
        super(ThreadPool, self).__init__()
        self.thread_count = thread_count if thread_count else 1

        # 任务队列和正在运行的线程列表
        self.working_list = list()
        self.func_list = Queue.Queue()

        # 结果队列
        self.result_queue = Queue.Queue()

        # 线程数量统计
        self.dead_thread_number = 0
        self.all_thread_number = 0

        # join和close标志
        self.joined = False
        self.closed = False

        # 退出标志
        self.exit = False
        self.already_exit = False

        # 开启主线程
        loop_thread = threading.Thread(target=self.__loop, name="ThreadPool.loop")
        # 如果开启了这个，主线程退出的时候loop就会终止
        loop_thread.daemon = False
        loop_thread.start()

        self.working_thread_number = 0

        # 线程池debug标志
        self.DEBUG = False

    def add_func(self, func, *args, **kwargs):
        self.func_list.put((func, args, kwargs))
        self.all_thread_number += 1

    def current_working_num(self):
        working = 0
        for thread in self.working_list:
            if thread.isAlive():
                # 线程还活着
                working += 1
            else:
                # 线程已经结束了
                logger.debug("Thread %s end." % thread.name)
                self.working_list.remove(thread)
                self.dead_thread_number += 1
        self.working_thread_number = working
        return working

    def __loop(self):
        while True:

            if self.exit:
                logger.debug("ThreadPool loop end.")
                break

            if self.joined and self.all_thread_number == self.dead_thread_number:
                self.terminated()

            if self.current_working_num() >= self.thread_count:
                # 没有空闲位置了
                time.sleep(1)
                logger.debug("No more place.") if self.DEBUG else None
                continue

            if self.func_list.empty():
                # 没有任务了
                time.sleep(1)
                logger.debug("No more task.") if self.DEBUG else None
                continue

            # 获取任务并运行
            task = self.func_list.get_nowait()
            try:
                thread_name = str(task[0].im_class).split(".")[-1].split("'")[0]
            except AttributeError:
                thread_name = task[0].__name__
            thread = threading.Thread(target=task[0], args=task[1], kwargs=task[2], name=thread_name)
            thread.start()
            logger.debug(thread_name + " start.") if self.DEBUG else None
            self.working_list.append(thread)

    def terminated(self):
        self.exit = True

    def close(self):
        self.closed = True

    def join(self):
        if self.closed:
            self.joined = True
        else:
            logger.fatal("Join must after closed thread pool.")
            os._exit(1)


