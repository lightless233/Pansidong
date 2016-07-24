#!/usr/bin/env python2
# coding: utf-8
# file: WebSpider
# time: 2016/7/17 10:59
import json
import random
import urlparse
import Queue
import time
import threading
from multiprocessing import cpu_count

import tldextract
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from bs4 import BeautifulSoup

from utils.ThreadPool2 import ThreadPool
from utils.SpiderBase import SpiderBase
from utils.data.LoggerHelp import logger

__author__ = "lightless"
__email__ = "root@lightless.me"


__all__ = ['WebSpider']


class WebSpider(SpiderBase):
    def __init__(self, target, deep=1, limit_domain=list(), thread_count=cpu_count()*2, phantomjs_count=cpu_count()):

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
        self.thread_count = thread_count
        self.phantomjs_count = phantomjs_count

        # 去重用的set
        self.url_set = set()
        # 存储爬虫结果的list
        self.links = list()
        # 待爬取的队列
        self.task_queue = Queue.Queue()
        self.spider_pool = None

        # 将初始目标置于待爬取的队列中
        self.task_queue.put((self.target, 0))

        # 统计信息
        self.raw_links_num = 0
        self.filter_links_num = 0
        self.links_num = 0

        # 初始化 webdriver
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        self.dcap["phantomjs.page.settings.resourceTimeout"] = 10
        self.dcap["phantomjs.page.settings.loadImages"] = False

        # self.driver = webdriver.PhantomJS(executable_path=self.phantomjs_path, desired_capabilities=self.dcap)
        # self.driver_lock = threading.Lock()

        # webdriver进程池
        logger.info("initial web spider phantomjs process pool...")
        self.driver_pool = list()
        self.driver_pool_lock = list()
        for i in range(self.phantomjs_count):
            self.driver_pool.append(
                webdriver.PhantomJS(executable_path=self.phantomjs_path, desired_capabilities=self.dcap)
            )
            self.driver_pool_lock.append(
                threading.Lock()
            )
            logger.info("%.2f%% finished." % ((float(i)*100)/float(self.phantomjs_count)))
        logger.info("initial finished.")

    def __del__(self):
        for driver in self.driver_pool:
            driver.quit()

    def do_spider(self):
        t = threading.Thread(target=self.start, name="WebSpider.start")
        t.start()

    def start(self):
        logger.debug("start of web spider.")

        # 开始线程池，并且开启了线程分发器
        self.spider_pool = ThreadPool(self.thread_count)
        # 开始爬取第一个页面
        self.spider_pool.add_func(self._start, target=self.task_queue.get_nowait())
        while True:

            if (not self.spider_pool.working_thread_number) and self.task_queue.empty():
                time.sleep(2)
                if (not self.spider_pool.working_thread_number) and self.task_queue.empty():
                    self.spider_pool.terminated()
                    logger.debug("WebSpider loop end.")
                    break

            if self.task_queue.empty():
                time.sleep(1)
                continue

            target = self.task_queue.get_nowait()
            self.spider_pool.add_func(self._start, target=(target[0], target[1]))
            time.sleep(0.1)

        logger.debug("end of web spider")

    def _start(self, target):
        logger.debug("start spider " + target[0])
        deep = target[1]
        target = target[0]

        # 随机取一个phantomjs进程
        phantomjs_tag = random.randint(0, self.phantomjs_count-1)

        self.driver_pool_lock[phantomjs_tag].acquire()
        retry_times = 2
        while retry_times:
            try:
                self.driver_pool[phantomjs_tag].get(target)
                break
            except:
                # driver.close()
                logger.error("retry %d" % retry_times)
                retry_times -= 1
                if not retry_times:
                    logger.warn("Time out when get %s HTML" % target)
                    self.driver_pool_lock[phantomjs_tag].release()
                    return
                else:
                    continue

        raw_html = self.driver_pool[phantomjs_tag].execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML"
        )
        http_log = json.loads(self.driver_pool[phantomjs_tag].get_log("har")[0]["message"])["log"]["entries"]
        self.driver_pool_lock[phantomjs_tag].release()

        soup = BeautifulSoup(raw_html, "html5lib")
        logger.debug("Get %s HTML done. Deep: %s" % (target, deep))

        for a in soup.find_all("a", href=True):
            a['href'] = a['href'].strip()
            if a['href'].startswith('javascript:') or a['href'].startswith('#') or not a['href']:
                continue
            self.raw_links_num += 1
            r = self.format_url(a['href'])
            # 如果该URL未出现过，并且在目标域中
            if r not in self.url_set:
                for domain in self.limit_domain:
                    ext = tldextract.extract(domain)
                    # *的时候匹配所有二级域名，或者只匹配特定的域名
                    if ((ext[0] == "*" or ext[0] == "") and tldextract.extract(a['href'])[1] == ext[1]) or \
                       (".".join(tldextract.extract(a['href'])) == domain):
                        self.filter_links_num += 1
                        self.url_set.add(r)
                        self.links.append(a['href'])
                        logger.debug(a['href'])
                        if deep + 1 <= self.deep:
                            self.task_queue.put((a['href'], deep + 1))

        for log in http_log:
            # logger.debug(" ".join([log['request']['method'], log['request']['url'], str(log['request']['queryString'])]))
            url = log['request']['url']
            self.raw_links_num += 1
            r = self.format_url(url)
            if r not in self.url_set:
                for domain in self.limit_domain:
                    ext = tldextract.extract(domain)
                    # *的时候匹配所有二级域名，或者只匹配特定的域名
                    if ((ext[0] == "*" or ext[0] == "") and tldextract.extract(url)[1] == ext[1]) or \
                       (".".join(tldextract.extract(url)) == domain):
                        self.filter_links_num += 1
                        self.url_set.add(r)
                        self.links.append(url)
                        logger.debug(url)
                        if deep + 1 <= self.deep:
                            self.task_queue.put((url, deep + 1))

        logger.debug("".join(["Raw links: ", str(self.raw_links_num)]))
        logger.debug("".join(["Filter links: ", str(self.filter_links_num)]))

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
