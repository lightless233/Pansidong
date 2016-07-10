#!/usr/bin/env python
# coding: utf-8

import codecs
import time
import ConfigParser

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.data.LoggerHelp import logger
from utils.data.Tables import Proxy

__author__ = "lightless"
__email__ = "root@lightless.me"


class SaveData(object):
    def __init__(self, results_queue, thread_pool, use_file=True, use_database=True, filename="proxy-ip-list.csv"):
        self.use_file = use_file
        self.use_database = use_database
        self.filename = filename
        self.results_queue = results_queue
        self.thread_pool = thread_pool

        if use_database:
            cf = ConfigParser.ConfigParser()
            cf.read("config.ini")
            db_name = cf.get("ProxySpider", "database")
            self.username = cf.get(db_name, "username")
            self.password = cf.get(db_name, "password")
            self.host = cf.get(db_name, "host")
            self.database = cf.get(db_name, "database")
            self.engine = create_engine("mysql://" + self.username + ":" + self.password + "@" +
                                        self.host + "/" + self.database + "?charset=utf8")
            self.db_session = sessionmaker(bind=self.engine)
            self.session = self.db_session()
        if use_file:
            self.ff = open(self.filename, "w")
            self.ff.write(codecs.BOM_UTF8)

    def __del__(self):
        if self.use_file:
            self.ff.close()
        if self.use_database:
            self.session.close()

    def write(self):
        # wait for other threads start.
        time.sleep(5)

        while not self.thread_pool.finished:
            if not self.results_queue.empty():
                res = self.results_queue.get(block=True)
                if self.use_file:
                    self.__write_file(res)
                if self.use_database:
                    self.__write_database(res)

    def __write_database(self, res):
        res = res[1]
        for r in res:
            new_proxy = Proxy(ip=r.get("ip", "None"), port=r.get("port", "None"), proxy_type=r.get("type", "None"),
                              location=r.get("location", "None"), protocol=r.get("protocol", "None"),
                              times=r.get("time", "None"), created_time=datetime.datetime.now(),
                              updated_time=datetime.datetime.now())
            try:
                self.session.add(new_proxy)
                self.session.commit()
            except Exception, e:
                logger.debug("save database error. " + e.message)

    def __write_file(self, res):
        self.ff.writelines(res[0].get('url') + "\n")
        self.ff.writelines("ip,port,type,protocol,location,time(s)\n")
        logger.info("[*] url: " + res[0].get('url'))
        res = res[1]
        for r in res:
            line = r.get('ip', 'None') + "," + r.get('port', 'None') + "," + \
                   r.get('type', 'None') + "," + r.get('protocol', 'None') + "," + \
                   r.get('location', 'None') + "," + r.get('time', 'None')
            logger.info("[*] " + line)
            self.ff.writelines((line + "\n").encode("utf8"))

