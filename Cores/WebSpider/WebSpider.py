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
    def __init__(self, target, deep=1, limit_domain=list(), thread_count=cpu_count()*2, phantomjs_count=cpu_count(),
                 filter_similar=False):

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
        self.filter_similar = filter_similar

        # 去重用的set
        self.url_set = set()
        self.url_filename_set = set()
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
        # dcap 好像无效
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        self.dcap["phantomjs.page.settings.resourceTimeout"] = 10
        self.dcap["phantomjs.page.settings.loadImages"] = False

        self.service_args = [
            "--webdriver-loglevel=DEBUG",
            "--webdriver-logfile=phantomjs.log"
            "--load-images=no",
            "--disk-cache=true"
        ]

        # webdriver进程池
        logger.info("initial web spider phantomjs process pool...")
        self.driver_pool = list()
        self.driver_pool_lock = list()
        for i in range(self.phantomjs_count):
            self.driver_pool.append(
                webdriver.PhantomJS(executable_path=self.phantomjs_path, desired_capabilities=self.dcap,
                                    service_args=self.service_args
                                    )
            )
            self.driver_pool_lock.append(
                threading.Lock()
            )
            logger.info("%.2f%% finished." % ((float(i + 1) * 100) / float(self.phantomjs_count)))
        logger.info("initial finished.")

    def __del__(self):
        for driver in self.driver_pool:
            driver.quit()
            del driver
        del self.driver_pool

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

        # 获取网页HTML
        raw_html = self.driver_pool[phantomjs_tag].execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML"
        )
        # 获取网页加载过程中发生的HTTP请求
        http_log = json.loads(self.driver_pool[phantomjs_tag].get_log("har")[0]["message"])["log"]["entries"]
        # 获取当前的页面URL
        base_url = self.driver_pool[phantomjs_tag].current_url
        self.driver_pool_lock[phantomjs_tag].release()

        soup = BeautifulSoup(raw_html, "html5lib")
        logger.debug("Get %s HTML done. Deep: %s" % (target, deep))

        # 处理文件中获取的href标签
        for a in soup.find_all("a", href=True):
            url = a['href'].strip()
            # 去掉非URL的部分
            if url.startswith('javascript:') or url.startswith('#') or not url:
                continue
            elif not url.startswith('https://') or not url.startswith('http://'):
                # 将相对路径转换为绝对路径
                url = urlparse.urljoin(base_url, url)
            self.check_same_url(url, deep, self.filter_similar)

        # 处理打开页面时产生的请求
        for log in http_log:
            url = log['request']['url']
            logger.error(url)
            self.check_same_url(url, deep, self.filter_similar)

        logger.debug("".join(["Raw links: ", str(self.raw_links_num)]))
        logger.debug("".join(["Filter links: ", str(self.filter_links_num)]))

    @staticmethod
    def format_url(url):
        """
        简单去重、去相似的URL
        :param url: 待处理的URL
        :return: URL的特征元组
        """

        # 规范化URL，在末尾增加 /
        if urlparse.urlparse(url)[2] == "":
            url += '/'

        url_structure = urlparse.urlparse(url)
        netloc = url_structure.netloc
        path = url_structure.path
        query = url_structure.query
        suffix = url_structure.path.split('.')[-1]

        result = (
            netloc,
            tuple([len(i) for i in path.split('/')]),
            tuple(sorted([i.split('=')[0] for i in query.split('&')])),
        )
        return result, suffix

    def check_same_url(self, url, deep, filter_similar):

        self.raw_links_num += 1

        # 先判断域名在不在目标域中
        if self.check_domain_limit(url):
            # 格式化url
            r, suffix = self.format_url(url)
            if suffix:
                # 有后缀，正常页面，根据是否判断相似性的设置继续判断
                if filter_similar and (r not in self.url_set):
                    self.filter_links_num += 1
                    self.url_set.add(r)
                    self.links.append(url)
                    logger.info(url)
                    if deep + 1 <= self.deep:
                        self.task_queue.put((url, deep + 1))
                elif not filter_similar and (url not in self.links):
                    self.filter_links_num += 1
                    self.links.append(url)
                    logger.info(url)
                    if deep + 1 <= self.deep:
                        self.task_queue.put((url, deep + 1))
            else:
                # 没有后缀，是个目录，去重，不去相似
                if url not in self.links:
                    self.filter_links_num += 1
                    self.links.append(url)
                    logger.info(url)
                    if deep + 1 <= self.deep:
                        self.task_queue.put((url, deep + 1))

    def check_domain_limit(self, url):
        for domain in self.limit_domain:
            ext = tldextract.extract(domain)
            # *的时候匹配所有二级域名，或者只匹配特定的域名
            if ((ext[0] == "*" or ext[0] == "") and tldextract.extract(url)[1] == ext[1]) or \
                    (".".join(tldextract.extract(url)) == domain):
                return True

        return False
