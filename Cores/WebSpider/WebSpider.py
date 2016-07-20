#!/usr/bin/env python2
# coding: utf-8
# file: WebSpider
# time: 2016/7/17 10:59
import urlparse
import Queue
import time

import tldextract
from selenium import webdriver
from bs4 import BeautifulSoup

from utils.ThreadPool import ThreadPool
from utils.SpiderBase import SpiderBase
from utils.data.LoggerHelp import logger

__author__ = "lightless"
__email__ = "root@lightless.me"


__all__ = ['WebSpider']


class WebSpider(SpiderBase):
    def __init__(self, target, deep=1, limit_domain=list()):

        # 设置phantomjs路径
        SpiderBase.__init__(self)
        SpiderBase.set_phantomjs_path(self)

        # 设置参数
        self.target = target
        self.deep = deep
        if limit_domain:
            self.limit_domain = limit_domain
        else:
            self.limit_domain = ".".join(tldextract.extract(self.target))

        # 去重用的set
        self.url_set = set()
        # 存储爬虫结果的list
        self.links = list()
        # 待爬取的队列
        self.task_queue = Queue.Queue()

        # 将初始目标置于待爬取的队列中
        self.task_queue.put((self.target, 0))

    def start(self):
        logger.debug("start of web spider.")
        # 创建线程池
        spider_thread_pool = ThreadPool(64)

        # 获取初始任务，队列中一定会存在这个task
        task = self.task_queue.get_nowait()
        # 开始第一个任务，不要阻塞这里
        spider_thread_pool.add_function(self._start, target=task)
        spider_thread_pool.run(join=False)
        logger.debug("没阻塞")
        while not spider_thread_pool.finished or not self.task_queue.empty():
            if not self.task_queue.empty():
                while not self.task_queue.empty():
                    task = self.task_queue.get_nowait()
                    # print task
                    # 判断URL的层数 并且 特征未出现过
                    if task[1] < self.deep:
                        spider_thread_pool.add_thread_list(self._start, target=task)

            time.sleep(1)
        logger.debug("end of web spider")

    def _start(self, target):
        logger.debug("start spider " + target[0])
        deep = target[1]
        target = target[0]

        service_args = [
            '--load-images=no',
        ]

        driver = webdriver.PhantomJS(executable_path=self.phantomjs_path, service_args=service_args)
        driver.get(target)
        raw_html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

        all_cnt = 0
        cnt = 0
        soup = BeautifulSoup(raw_html, "html5lib")
        logger.debug("Get HTML done.")

        for a in soup.find_all("a", href=True):
            a['href'] = a['href'].strip()
            if a['href'].startswith('javascript:') or a['href'].startswith('#') or not a['href']:
                continue
            all_cnt += 1
            r = self.format_url(a['href'])
            # 如果该URL未出现过，并且在目标域中
            if r not in self.url_set:
                for domain in self.limit_domain:
                    ext = tldextract.extract(domain)
                    # *的时候匹配所有二级域名，或者只匹配特定的域名
                    if ((ext[0] == "*" or ext[0] == "") and tldextract.extract(a['href'])[1] == ext[1]) or \
                       (".".join(tldextract.extract(a['href'])) == domain):
                        cnt += 1
                        self.url_set.add(r)
                        self.links.append(a['href'])
                        self.task_queue.put((a['href'], deep + 1))

        logger.debug("".join(["All links: ", str(all_cnt)]))
        logger.debug("".join(["Get links: ", str(cnt)]))

    @staticmethod
    def format_url(url):
        """
        简单去重、去相似的URL
        :param url: 待处理的URL
        :return: URL的特征元组
        """

        if urlparse.urlparse(url)[2] == "":
            url += '/'

        url_structure = urlparse.urlparse(url)
        netloc = url_structure[1]
        path = url_structure[2]
        query = url_structure[4]

        result = (
            netloc,
            tuple([len(i) for i in path.split('/')]),
            tuple(sorted([i.split('=')[0] for i in query.split('&')]))
        )
        return result
