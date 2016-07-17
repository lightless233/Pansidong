#!/usr/bin/env python2
# coding: utf-8
# file: WebSpider
# time: 2016/7/17 10:59
import urlparse

from selenium import webdriver
from bs4 import BeautifulSoup

from utils.SpiderBase import SpiderBase
from utils.data.LoggerHelp import logger

__author__ = "lightless"
__email__ = "root@lightless.me"


__all__ = ['WebSpider']


class WebSpider(SpiderBase):
    def __init__(self, target, deep=None):
        SpiderBase.__init__(self)
        SpiderBase.set_phantomjs_path(self)
        self.target = target
        self.deep = deep
        self.url_set = set()
        self.links = list()

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
            if r not in self.url_set:
                cnt += 1
                self.url_set.add(r)
                self.links.append(a['href'])

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
