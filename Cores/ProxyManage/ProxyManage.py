#!/usr/bin/env python
# coding: utf-8

import sys
import datetime
import time
import Queue
import platform

import requests
import prettytable
from sqlalchemy.exc import SQLAlchemyError

from utils.Data.LoggerHelp import logger
from utils.DBConnection import DBConnection
from utils.Data.Tables import Proxy
from utils.ThreadPool2 import ThreadPool

__author__ = "lightless"
__email__ = "root@lightless.me"


class ProxyManage(object):

    def __init__(self, **kwargs):
        """
        初始化代理地址检查
        :param kwargs:
                        all: True: 检测数据库中全部的IP, False：检测指定的IP列表，以逗号分隔
                        ips: 待检测的IP，"1.1.1.1:80, 2.2.2.2:3128"
        """
        super(ProxyManage, self).__init__()

        # request headers
        self.headers = {
            'User-Agent': 'curl/7.49.1',
        }

        # 初始化数据库连接
        db = DBConnection.DBConnection()
        db.connect()
        self.session = db.session

        # 获取参数
        self.kwargs = kwargs

        # 检测全部IP时的线程池
        self.thread_pool = None

        self.result_queue = Queue.Queue()

    def __del__(self):
        del self.session

    def check(self):
        """
        根据参数检测ip或数据库中的ip列表存活性
        :rtype: None
        """
        if self.kwargs.get("all", None) is not None:
            # 检查数据库中的全部ip
            self._check_ip_all()
        elif self.kwargs.get("ips", None) is not None:
            # 检查提供的IP
            self._check_ip_list(self.kwargs.get("ips"))

    def _check(self, ip, port, save_to_queue=False):
        """
        检测给定的代理IP和端口是否存活
        :param ip: 代理IP
        :param port: 代理端口
        :param save_to_queue: 如果设置为True，则存储到结果队列中，否则不存储，默认为False
        :return: success, delay 如果目标代理存活，则success为True且delay为延迟，否则为False，delay为0
        """
        # 检查参数合法性
        if ip == "" or port == "":
            logger.error("Invalid ip or port found. Skipping...")
            return False, -1.0

        # 3次重试机会
        retry = 3
        time_summary = 0.0
        success = False
        while retry:
            logger.debug("Times: {0}. Trying {1}:{2} connection...".format(3-retry+1, ip, port))
            proxies = {
                'http': ip + ":" + port
            }

            try:
                time_start = time.time()
                requests.get("http://ip.cn/", headers=self.headers, proxies=proxies, timeout=10)
                time_summary = time.time() - time_start
                success = True
                break
            except requests.RequestException:
                logger.warning("{0}:{1} proxy time out.".format(ip, port))
                continue
            finally:
                retry -= 1
        if save_to_queue:
            self.result_queue.put((ip, port, success, time_summary))
        return success, time_summary

    def _check_ip_list(self, raw_ips):
        try:
            if raw_ips is not None and len(raw_ips):
                ips = raw_ips.split(",")
                for ip in ips:
                    ip_stu = ip.strip().split(":")
                    s, t = self._check(ip_stu[0], ip_stu[1])
                    logger.info("IP {0} Connect {1}, time: {2:.2f}s".format(ip, "success", t)) if s \
                        else logger.error("IP {0} Connect failed.".format(ip))
                    self._update_db(ip_stu[0], ip_stu[1], t, s)
            else:
                logger.fatal("No IP provide.")
                sys.exit(1)
        except KeyError:
            logger.fatal("No IP provide.")
            sys.exit(1)

    def _check_ip_all(self):
        rows = self.session.query(Proxy).all()
        self.thread_pool = ThreadPool(thread_count=10 if not len(rows)/20 else len(rows)/20)
        for row in rows:
            self.thread_pool.add_func(self._check, ip=row.ip, port=row.port, save_to_queue=True)
        self.thread_pool.close()
        self.thread_pool.join()
        while True:
            if self.thread_pool.exit is True and self.result_queue.empty():
                break
            else:
                try:
                    res = self.result_queue.get_nowait()
                    ip = res[0]
                    port = res[1]
                    delay = res[3]
                    alive = res[2]
                    logger.info("IP {0} Connect {1}, time: {2:.2f}s".format(ip, "success", delay)) if alive \
                        else logger.error("IP {0} Connect failed.".format(ip))
                    self._update_db(ip, port, delay, alive)
                except Queue.Empty:
                    time.sleep(2)

    def _update_db(self, ip, port, delay, alive):
        proxy_item = self.session.query(Proxy).filter(Proxy.ip == ip, Proxy.port == port).all()
        if len(proxy_item):
            # 数据库中已经有这个IP了，更新即可
            proxy_item = proxy_item[0]
            proxy_item.updated_time = datetime.datetime.now()
            proxy_item.times = delay
            proxy_item.is_alive = 1 if alive else 0
            try:
                self.session.add(proxy_item)
                self.session.commit()
            except SQLAlchemyError, e:
                logger.error("Error while update proxy information to database.")
                logger.error(e.message)
                sys.exit(1)
        elif not len(proxy_item):
            # 数据库中没有IP，添加进去
            new_proxy = Proxy(
                ip=ip, port=port, proxy_type=None, location=None, protocol=None, times=delay, is_alive=1,
                created_time=datetime.datetime.now(), updated_time=datetime.datetime.now()
            )
            try:
                self.session.add(new_proxy)
                self.session.commit()
            except SQLAlchemyError, e:
                logger.error("Error while update proxy information to database.")
                logger.error(e.message)
                sys.exit(1)

    def get_alive_proxy(self, amount=0, delay=0):
        """
        从数据库中获取获取存活的代理
        :param amount: 取出的数量
        :param delay: 取出延时小于delay的代理
        """
        all_ips = self.session.query(Proxy)
        all_ips = all_ips.filter(Proxy.is_alive == "1")
        if int(delay):
            all_ips = all_ips.filter(Proxy.times < delay)
        all_ips = all_ips.order_by(Proxy.times)
        if int(amount):
            all_ips = all_ips.limit(amount)

        result = all_ips.all()
        # TODO：在Windows上要设置GBK编码，mac未测试。
        # Linux 上需要设置为UTF-8编码
        encoding = "UTF-8" if "linux" in platform.system().lower() else "GBK"
        x = prettytable.PrettyTable(encoding=encoding, field_names=["Proxy IP", "Location", "Proxy Type", "Delay (s)"],
                                    float_format=".2")
        for res in result:
            x.add_row([res.ip + ":" + res.port, res.location, res.proxy_type, float(res.times)])
        x.align = "l"
        print x
        print "[*] Total: {}".format(str(len(result)))

    def clean_dead_proxy(self):
        try:
            logger.info("Start clean dead proxy in db.")
            dead_proxy = self.session.query(Proxy).filter(Proxy.is_alive == "0").all()
            logger.info("Found {} dead proxy in db.".format(len(dead_proxy)))
            for dp in dead_proxy:
                self.session.delete(dp)
            self.session.commit()
            logger.info("Clean done. {} dead proxies cleaned.".format(len(dead_proxy)))
        except SQLAlchemyError:
            logger.fatal("Error occurred when clean dead proxy from db.")
            sys.exit(1)
