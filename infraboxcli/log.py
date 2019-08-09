from __future__ import print_function

import traceback

from colorama import Fore

from .Utils import InfraBoxCLIException


class Logger(object):
    def __init__(self):
        pass

    @staticmethod
    def _print(color, s, *args, **kwargs):
        print("%s[infrabox] %s%s" % (color, s, Fore.RESET), *args, **kwargs)

    @staticmethod
    def log(s, print_header=True, *args, **kwargs):
        print("%s%s" % ("[infrabox] " if print_header else "", s), *args, **kwargs)

    def info(self, s, *args, **kwargs):
        self._print(Fore.BLUE, s, *args, **kwargs)

    def warn(self, s, *args, **kwargs):
        self._print(Fore.YELLOW, s, *args, **kwargs)

    def error(self, s, raise_exception=True, *args, **kwargs):
        self._print(Fore.RED, s, *args, **kwargs)
        if raise_exception:
            raise LoggerError

    def exception(self):
        msg = traceback.format_exc()
        self.error(msg, False)


class LoggerError(InfraBoxCLIException):
    pass


logger = Logger()
