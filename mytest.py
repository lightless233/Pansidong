#!/usr/bin/env python2
# coding: utf-8
# file: mytest.py
# time: 2016/7/13 21:34
import json
import threading
import time

import tldextract
from selenium.webdriver import DesiredCapabilities

from Cores.ProxySpider.ProxySpider import ProxySpider
from Cores.WebSpider.WebSpider import WebSpider



# ps = ProxySpider()
# ps.load()
# ps.start()
#
# pm = ProxyManage()
# pm.check()

# proxies = {
#     "http": "113.124.68.42:8998",
# }
#
# headers = {
#     'User-Agent': 'curl/7.49.1',
# }
#
# start_time = time.time()
# r = requests.get("http://ip.cn", headers=headers, proxies=proxies)
# elapsed_time = time.time() - start_time
# print elapsed_time
# print r.content

# for i in xrange(10):
#     print i
#     try:
#         x = i / 0
#         print "try here"
#     except Exception, e:
#         print e.message
#         continue
#     finally:
#         print "finally here"
#     print "try here 2"
from utils.data.LoggerHelp import logger

web_spider = WebSpider("http://www.china-pub.com", limit_domain=['*.china-pub.com'], deep=2, thread_count=50)
web_spider.do_spider()
# web_spider.start()
# while True:
#     time.sleep(1)
#     print web_spider.links
# time.sleep(1)
while True:
    time.sleep(5)
    logger.debug("Alive thread: %d" % web_spider.spider_pool.working_thread_number)
    logger.debug("Left tasks number: %d" % web_spider.task_queue.qsize())
    logger.debug("links num before filter: %d" % web_spider.raw_links_num)
    logger.debug("links num after filter: %d" % web_spider.filter_links_num)


    if web_spider.spider_pool.working_thread_number == 0:
        break
#
# print web_spider.links
with open("urls.txt", "w") as ff:
    for url in web_spider.links:
        ff.write(url.decode('utf8') + "\n")

# urls = ['www.lightless.me', 'www.baidu.com']
# jobs = [gevent.spawn(socket.gethostbyname, url) for url in urls]
# # gevent.joinall(jobs)
# res = [job.value for job in jobs]
# print res
#
# def func():
#     return '123'
#
# tp = ThreadPool()
# tp.add_task_run(socket.gethostbyname, 'www.lightless.me')
# tp.add_task_run(socket.gethostbyname, 'www.baidu.com')
# # tp.add_task_run(func)
#
# print tp.value.get().value
# print tp.value.get().value
# # print tp.value.get().value


# from selenium import webdriver
#
# service_args = [
#     '--load-images=no',
# ]
# dcap = dict(DesiredCapabilities.PHANTOMJS)
# dcap["phantomjs.page.settings.resourceTimeout"] = 10
# dcap["phantomjs.page.settings.loadImages"] = False
# driver = webdriver.PhantomJS(executable_path='ThirdParty/phantomjs/phantomjs.exe', service_args=service_args)
# driver.get("http://www.china-pub.com")
# x = driver.get_log('har')

# d = json.loads(x[0]['message'])
# print d
# print type(d)
# print d.keys()
# print "====="
# print d['log']
# print d['log'].keys()
# print "=== entries ==="
# print d['log']['entries']
# print d['log']['entries'][0].keys()
# print d['log']['entries'][0]['request'].keys()
# print d['log']['entries'][0]['request']['url']
# print d['log']['entries'][0]['request']['cookies']
# print d['log']['entries'][0]['request']['queryString']
# print d['log']['entries'][0]['request']['method']
# print d['log']['entries'][0]['request']['headers']

# for i in d['log']['entries']:
#     print i['request']['method'], i['request']['url'], i['request']['queryString']
#
# for i in d['log']['pages']:
#     print i['id']
# reqMonitoring = json.loads(driver.get_log("har")[0]["message"])["log"]["entries"]
# print reqMonitoring
# for i in reqMonitoring:
#     print i['request']['method'], i['request']['url'], i['request']['queryString']
#
# driver.quit()




