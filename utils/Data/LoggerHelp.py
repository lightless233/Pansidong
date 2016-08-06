#!/usr/bin/env python
# coding: utf-8

import colorlog
import logging

__author__ = "lightless"
__email__ = "root@lightless.me"

__all__ = ['logger']


handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(levelname)s] [%(threadName)s] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s',
        datefmt="%H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
    )
)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel("DEBUG")
