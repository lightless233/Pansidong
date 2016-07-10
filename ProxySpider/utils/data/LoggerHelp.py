#!/usr/bin/env python
# coding: utf-8
import logging
import ConfigParser

__author__ = "lightless"
__email__ = "root@lightless.me"


formatter = logging.Formatter("[%(levelname)s] [(%(threadName)s)] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", "%H:%M:%S")

console = logging.StreamHandler()
console.setFormatter(formatter)

logger = logging.getLogger("ProxySpiderLogger")
logger.addHandler(console)

cf = ConfigParser.ConfigParser()
cf.read("config.ini")
if cf.has_option("ProxySpider", "debug") and cf.get("ProxySpider", "debug") == "On":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
