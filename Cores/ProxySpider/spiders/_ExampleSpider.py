#!/usr/bin/env python
# coding: utf-8

__author__ = "lightless"
__email__ = "root@lightless.me"

"""
爬虫插件类

命名规则：
      文件名与类名相同。因为本文件仅作为示例，所以文件名以下划线开头，在编写自己的插件时请注意，以下划线开头的插件文件是不会被加载进框架的。

实现函数：
      __init__
            构造函数
      run
          爬取函数，结果集为列表，第一项为字典，存储基本信息，第二项为列表，其中每一项均为字典，
          字典中应当包括：ip，port，type，location，time
          ip： 代理地址的IP
          port： 代理地址的端口
          type： 代理类型，一般为 "透明，匿名，高匿" 其中之一，根据自己爬取的结果填充，若所爬页面未提供该值，填充为None即可。
          protocol： 代理支持的协议，HTTP/HTTPS，根据爬取的结果进行填充，若未提供该值，填充为None。
          location： 该代理IP的位置，根据自己爬取的结果进行填充，若所爬页面未提供该值，填充为None即可。
          time： 该代理IP的响应时间，单位为秒。
          结果集格式如下：
          [
            {"url": self.url, "type": self.type, "tag": self.tag},
            [
                {"ip": "33.44.55.66", "port": "80", "type": "高匿", "protocol": "HTTP", "location": "中国 江苏省 苏州市 电信", "time": "0.3"},
                {"ip": "11.22.33.44", "port": "3128", "type": "透明", "protocol": "HTTPS", "location": "中国 河南省 洛阳市 电信", "time": "2.7"},
                {"ip": "22.33.44.55", "port": "8888", "type": "匿名", "protocol": "HTTP/HTTPS", "location": "Taiwan", "time": "5.6"},
                ...
            ]
          ]
      set_result_queue
          设置结果队列，复制example中的函数即可，一般不需要修改。

      类外实现函数：get_spider_class
          返回爬虫类，按照example中的写法即可。
"""


class ExampleSpider:
    def __init__(self):
        # 待爬取的URL
        self.url = "Your url here."
        # 代理类型，包括HTTP，shadowsocks，VPN
        self.type = "HTTP"
        # 一些你自己的备注，建议填写以作区分
        self.tag = "鲲鹏-全球-高匿代理"
        # Result Queue
        self.result_queue = None

    def set_result_queue(self, result_queue):
        self.result_queue = result_queue

    def run(self):
        # TODO: Add your process here...
        # TODO: delete these lines below, just an example...
        t = []
        s = {"ip": "11.22.33.44", "port": "8080", "type": u"透明", "protocol": "HTTP", "location": u"Taiwan", "time": "2.6"}
        t.append(s)
        s = {"ip": "22.33.44.55", "port": "3128", "type": u"高匿", "protocol": "HTTPS/HTTP", "location": u"江苏省南京市 联通", "time": "5"}
        t.append(s)
        tt = [{
            "url": self.url,
            "type": self.type,
        }, t]
        self.result_queue.put(tt)


def get_spider_class():
    return ExampleSpider

