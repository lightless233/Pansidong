#!/usr/bin/env python2
# coding: utf-8
# file: DBConnection.py
# time: 2016/8/6 15:16

import sys
import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.Data import Enum
from utils.Data.LoggerHelp import logger

__author__ = "lightless"
__email__ = "root@lightless.me"

__all__ = ["DBConnection", "DB_TYPE"]


DB_TYPE = Enum.Enum([
    "MYSQL",
])


class DBConnection(object):
    
    def __init__(self):
        super(DBConnection, self).__init__()
        self._type, self._username, self._password, self._host, self._database = self._get_db_config()
        self._engine = None
        self._db_session = None
        self.session = None

    def __del__(self):
        del self._engine
        del self._db_session
        del self.session

    def connect(self):
        if self._type.upper() == DB_TYPE.MYSQL:
            self._engine = create_engine(
                "mysql://" + self._username + ":" + self._password + "@" +
                self._host + "/" + self._database + "?charset=utf8"
            )
            self._db_session = sessionmaker(bind=self._engine)
            self.session = self._db_session()
        else:
            logger.fatal("Unsupported database type.")
            sys.exit(1)

    @staticmethod
    def _get_db_config():
        cf = ConfigParser.ConfigParser()
        cf.read("config.ini")
        db_type = cf.get("Pansidong", "database")
        username = cf.get(db_type, "username")
        password = cf.get(db_type, "password")
        host = cf.get(db_type, "host")
        database = cf.get(db_type, "database")
        return db_type, username, password, host, database
