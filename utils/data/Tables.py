#!/usr/bin/env python2
# coding: utf-8

from sqlalchemy import Column
from sqlalchemy import String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base


__author__ = "lightless"
__email__ = "root@lightless.me"


Base = declarative_base()


class Proxy(Base):

    __tablename__ = "proxy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String(16), index=True, default=None, nullable=True)
    port = Column(String(5), default=None, nullable=True)
    proxy_type = Column(String(32), default=None, nullable=True)
    location = Column(String(128), default=None, nullable=True)
    protocol = Column(String(64), default=None, nullable=True)
    times = Column(Float, default=None, nullable=True)
    created_time = Column(DateTime, default=None, nullable=True)
    updated_time = Column(DateTime, default=None, nullable=True)

