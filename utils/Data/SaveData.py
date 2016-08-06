#!/usr/bin/env python
# coding: utf-8

import codecs
import os
import time
import ConfigParser
import sys
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.Data.LoggerHelp import logger
from utils.Data.Tables import Proxy

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
            try:
                cf = ConfigParser.ConfigParser()
                cf.read("config.ini")
                db_name = cf.get("Pansidong", "database")
                username = cf.get(db_name, "username")
                password = cf.get(db_name, "password")
                host = cf.get(db_name, "host")
                database = cf.get(db_name, "database")
            except AttributeError, e:
                logger.fatal(e.message)
                sys.exit(1)
            self.engine = create_engine("mysql://" + username + ":" + password + "@" +
                                        host + "/" + database + "?charset=utf8")
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
            # 先检测数据库中是否存在该IP
            # 如果IP和端口均相同
            # 则认为是重复的数据，不添加到数据库中

            proxy = self.session.query(Proxy).filter_by(ip=r.get("ip"), port=r.get("port")).first()
            if proxy:
                proxy.updated_time = datetime.datetime.now()
                try:
                    self.session.add(proxy)
                    self.session.commit()
                except Exception, e:
                    logger.debug("Update database error. " + e.message)
                continue

            new_proxy = Proxy(ip=r.get("ip", "None"), port=r.get("port", "None"), proxy_type=r.get("type", "None"),
                              location=r.get("location", "None"), protocol=r.get("protocol", "None"),
                              times=r.get("time", "None"), is_alive=0, created_time=datetime.datetime.now(),
                              updated_time=datetime.datetime.now())
            try:
                self.session.add(new_proxy)
                self.session.commit()
            except Exception, e:
                logger.debug("Save database error. " + e.message)

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

