#!/usr/bin/env python2
# coding: utf-8
import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.Data.LoggerHelp import logger
from utils.Data.Tables import Proxy

__author__ = "lightless"
__email__ = "root@lightless.me"


if __name__ == "__main__":
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    db_name = cf.get("Pansidong", "database")
    username = cf.get(db_name, "username")
    password = cf.get(db_name, "password")
    host = cf.get(db_name, "host")
    database = cf.get(db_name, "database")

    engine = create_engine("mysql://" + username + ":" + password + "@" + host + "/" + database)
    db_session = sessionmaker(bind=engine)
    try:
        Proxy.metadata.create_all(engine)
        logger.debug("Tables create success.")
    except Exception, e:
        logger.error(e.message)


