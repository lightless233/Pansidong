#!/usr/bin/env python
# coding: utf-8
import logging
import ConfigParser

import coloredlogs
import sys

__author__ = "lightless"
__email__ = "root@lightless.me"

__all__ = ['logger']

FIELD_STYLES = dict(
    asctime=dict(color='green'),
    hostname=dict(color='magenta'),
    levelname=dict(color='green', bold=coloredlogs.CAN_USE_BOLD_FONT),
    filename=dict(color='magenta'),
    name=dict(color='blue'),
    threadName=dict(color='green')
)

LEVEL_STYLES = dict(
    debug=dict(color='green'),
    info=dict(color='cyan'),
    verbose=dict(color='blue'),
    warning=dict(color='yellow'),
    error=dict(color='red'),
    critical=dict(color='red', bold=coloredlogs.CAN_USE_BOLD_FONT)
)
logger = logging.getLogger("Pansidong")

cf = ConfigParser.ConfigParser()
cf.read("config.ini")
if cf.has_option("Pansidong", "debug") and cf.get("Pansidong", "debug") == "On":
    level = "DEBUG"
else:
    level = "INFO"

coloredlogs.install(
    level=level,
    logger=logger,
    stream=sys.stdout,
    fmt="[%(levelname)s] [(%(threadName)s)] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S",
    level_styles=LEVEL_STYLES,
    field_styles=FIELD_STYLES,
)
