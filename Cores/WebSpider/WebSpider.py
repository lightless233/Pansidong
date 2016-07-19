#!/usr/bin/env python2
# coding: utf-8
# file: WebSpider
# time: 2016/7/17 10:59
import urlparse
import Queue

import tldextract
from selenium import webdriver
from bs4 import BeautifulSoup

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
        self.wait_queue = Queue.Queue()

    def start(self):
        logger.debug(self.target)

        service_args = [
            '--load-images=no',
        ]

        driver = webdriver.PhantomJS(executable_path=self.phantomjs_path, service_args=service_args)
        driver.get(self.target)
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
                        self.wait_queue.put(a['href'])

        logger.debug("".join(["All links: ", str(all_cnt)]))
        logger.debug("".join(["Get links: ", str(cnt)]))

    @staticmethod
    def format_url(url):

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
