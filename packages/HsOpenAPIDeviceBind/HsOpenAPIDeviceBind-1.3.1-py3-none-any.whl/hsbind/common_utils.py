#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

def get_info_logger(name, filename: str=None):
    handler = logging.StreamHandler() if filename is None else logging.FileHandler(filename=filename)
    return get_logger(name, level=logging.INFO, handler=handler)

def get_debug_logger(name, filename: str=None):
    handler = logging.StreamHandler() if filename is None else logging.FileHandler(filename=filename)
    return get_logger(name, level=logging.DEBUG, handler=handler)

def get_warn_logger(name, filename: str=None):
    handler = logging.StreamHandler() if filename is None else logging.FileHandler(filename=filename)
    return get_logger(name, level=logging.WARN, handler=handler)

def get_error_logger(name, filename: str=None):
    handler = logging.StreamHandler() if filename is None else logging.FileHandler(filename=filename)
    return get_logger(name, level=logging.ERROR, handler=handler)

def get_logger(name, level=logging.INFO, handler=logging.StreamHandler()):
    LOG_FORMAT = "%(asctime)s.%(msecs)03d - %(levelname)s - [%(processName)s|%(threadName)s] - [%(filename)s - %(funcName)s] - line %(lineno)s: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    logger = logging.getLogger(name)  # __name__
    logger.setLevel(level=level)
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
