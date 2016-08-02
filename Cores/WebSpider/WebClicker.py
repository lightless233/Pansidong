#!/usr/bin/env python2
# coding: utf-8
# file: WebSpider
# time: 2016/08/02 23:18

import Queue
import threading
import time

from utils.data.LoggerHelp import logger

__author__ = "lightless"
__email__ = "root@lightless.me"

__all__ = ["WebClicker"]


class WebClicker(object):
    def __init__(self):
        super(WebClicker, self).__init__()

        # 工作队列
        self.work_queue = Queue.Queue()
        # 退出标志
        self._exit = False

    def add_url(self, url):
        self.work_queue.put(url)

    def click_engine(self):
        # 开个新线程进行循环，不要阻塞
        click_thread = threading.Thread(target=self._loop, name="ClickLoopThread")
        click_thread.start()

    def terminate(self):
        self._exit = True
        logger.info("Send exit to WebClicker..Wait for quit.")

    def _loop(self):
        while True:
            # 如果检测到退出标志，则退出
            if self._exit:
                break

            target_url = None
            try:
                target_url = self.work_queue.get(block=True, timeout=1)
            except Queue.Empty:
                time.sleep(5)



