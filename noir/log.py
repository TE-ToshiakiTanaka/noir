import os
import sys
import logging
import traceback

from noir.exception import *

BASE_FORMAT = '%(processName)s.%(name)s ( PID %(process)d ) : %(asctime)s - %(levelname)s - %(message)s'

class LogLevel(object):
    LOG_LEVEL_MAP = {'d' : {'level': logging.DEBUG,
                            'color': '\033[92m '},
                     'i' : {'level': logging.INFO,
                            'color': '\033[94m '},
                     'w' : {'level': logging.WARNING,
                            'color': '\033[93m '},
                     'e' : {'level': logging.ERROR,
                            'color': '\033[91m '},
                     'c' : {'level': logging.CRITICAL,
                            'color': '\033[95m '}
                    }
    @classmethod
    def get_level_name(cls, level):
        return cls.LOG_LEVEL_MAP[cls.verify_level(level)]['level']

    @classmethod
    def get_ancii_string(cls, level, string):
        return '%s%s%s' % (cls.LOG_LEVEL_MAP[cls.verify_level(level)]
                           ['color'], string, ' \033[0m')

    @classmethod
    def verify_level(cls, level):
        lvl = str(level).lower()
        if lvl in cls.LOG_LEVEL_MAP:
            return lvl
        else:
            raise LogError({
                'cmd'       : None,
                'out'       : level,
                'message'   : 'Log level "%s" not an accepted level, accepted levels: %s' % (lvl, cls.LOG_LEVEL_MAP.keys())})

class Log(object):
    def __init__(self, name, level=logging.DEBUG, format=BASE_FORMAT, shell=True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.shell = shell
        self.addHandler(self.consoleHandler(format, level))

    def addHandler(self, handler):
        self.logger.addHandler(handler)

    @classmethod
    def consoleHandler(self, format, level):
        f = logging.Formatter(format)
        h = logging.StreamHandler()
        h.setLevel(level)
        h.setFormatter(f)
        return h

    @classmethod
    def fileHandler(self, filename, format, level):
        if not os.path.exists(filename):
            raise LogError("Log file '%s' is not found." % filename)
        fo = logging.Formatter(format)
        h = logging.FileHandler(filename, 'a+')
        h.setLevel(level)
        h.setFormatter(fo)
        return h

    def traceback(self, level=logging.CRITICAL):
        _, _, _tb = sys.exc_info()
        stack_trace = traceback.extract_tb(_tb)
        self.log(level, "Stack Trace:")
        for stack_item in stack_trace:
            self.log(level, ' %s' % str(stack_item))

    def log(self, level, message):
        try:
            if self.shell: message = LogLevel.get_ancii_string(level, message)
            if LogLevel.get_level_name(level) == logging.DEBUG: self.logger.debug(message)
            elif LogLevel.get_level_name(level) == logging.INFO: self.logger.info(message)
            elif LogLevel.get_level_name(level) == logging.WARNING: self.logger.warning(message)
            elif LogLevel.get_level_name(level) == logging.ERROR: self.logger.error(message)
            else: self.logger.critical(message)
        except LogError as e:
            self.traceback('c')

    def debug(self, message): self.log('d', message)
    def info(self, message): self.log('i', message)
    def warning(self, message): self.log('w', message)
    def error(self, message): self.log('e', message)
    def critical(self, message): self.log('c', message)

LOG = Log("System.NOIR")
