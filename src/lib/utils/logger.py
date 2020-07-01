#!/usr/bin/env python3
import sys
import os
import importlib

import logging
from logging.handlers import RotatingFileHandler

INFO = logging.INFO
WARNING = logging.WARNING
DEBUG = logging.DEBUG
ERROR = logging.ERROR

class Logger():
    def __init__(self, log_path, log_rotation_files, log_file_debug, log_file_cron):
        self.handlers = {}

        self.logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
        self.rootLogger = logging.getLogger()

        self.fileHandler = RotatingFileHandler(f"{log_path}/{log_file_debug}", maxBytes=32000, backupCount=log_rotation_files)
        self.fileHandler.setFormatter(self.logFormatter)

        self.CRON_HANDLER = RotatingFileHandler(f"{log_path}/{log_file_cron}", maxBytes=32000, backupCount=log_rotation_files)
        self.CRON_HANDLER.setFormatter(self.logFormatter)

        self.handlers["CRON_HANDLER"] = self.CRON_HANDLER

        self.rootLogger.addHandler(self.fileHandler)
#        self.rootLogger.addHandler(self.CRON_HANDLER)

        self.rootLogger.setLevel(logging.INFO)

    def add_handler(self, handler):
        self.rootLogger.addHandler(self.handlers[handler])

def load(log_path, log_rotation_files = 5):
    global logger

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file_debug = "debug.log"
    log_file_cron = "cron.log"

    logger = Logger(log_path, log_rotation_files, log_file_debug, log_file_cron)
    #set_level(INFO)
    debug("Logger initialized!")

def add_handler(handler):
    global logger
    logger.add_handler(handler)

def log(level, s, **kwargs):
    if not "logger" in globals():
        raise ValueError("Logger not loaded")

    if not isinstance(levels, list):
       level = [level]

    log_func = {
        logging.debug : debug,
        logging.info : info,
        logging.warning : warning,
        logging.error : error
    }

    log_func[level](s, **kwargs)

def log_print(level, s, **kwargs):
    log(level, s, **kwargs)
    print(s)

def set_level(level):
    logger.rootLogger.level = level

def info(s, **kwargs):
 #   if not "logger" in globals():
#        raise ValueError("Logger not loaded")
    logger.rootLogger.info(s)

def info_print(s, **kwargs):
 #   if not "logger" in globals():
#        raise ValueError("Logger not loaded")

    info(s, **kwargs)
    print(s)

def warning(s, **kwargs):
    if not "logger" in globals():
        raise ValueError("Logger not loaded")

    logging.warning(s, **kwargs)

def warning_print(s, **kwargs):
    warning(s, **kwargs)
    print(s)

def debug(s, **kwargs):
    logging.debug(s, **kwargs)

def debug_print(s, **kwargs):
    debug(s, **kwargs)
    print(s)

def error(s, **kwargs):
    logging.error(s, **kwargs)

def error_print(s, **kwargs):
    error(s, **kwargs)
    print(s)


