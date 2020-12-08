import functools
import logging
import os
from pathlib import Path

import appdirs
import arrow
from zmq.log.handlers import PUBHandler

from snout.api import classproperty
from snout.api.event import SnoutEventHandler

LOG_LEVEL_FILE = logging.DEBUG
LOG_LEVEL_STREAM = logging.ERROR  # logging.DEBUG
LOG_LEVEL_EVENT = logging.DEBUG


class StaticLogger:
    # TODO: Clean global logger up
    _logger = None

    @classproperty
    def logger(cls):
        if not cls._logger:
            cls._logger = logging.getLogger('Snout')
            cls._logger.setLevel(LOG_LEVEL_STREAM)
            ch = logging.StreamHandler()
            ch.setLevel(LOG_LEVEL_STREAM)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            cls._logger.addHandler(ch)
        return cls._logger


class Logger(object):
    """Logger provides universal logging functionality to all application classes.

    Attributes:
        logger (logging.Logger): A global logger for Snout that can be used outside of class instances
    """

    _zh = PUBHandler('tcp://127.0.0.1:12345')

    def __init__(self, *args, **kwargs):
        # TODO: Fine tune logging setup https://docs.python.org/3/howto/logging-cookbook.html

        self.agent = kwargs.get('agent', None)

        log_level_file = kwargs.get('log_level_file', LOG_LEVEL_FILE)
        log_level_stream = kwargs.get('log_level_file', LOG_LEVEL_STREAM)
        log_level_event = kwargs.get('log_level_ui', LOG_LEVEL_EVENT)
        try:
            self._logger = logging.getLogger(self.fullname)
        except AttributeError:
            self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # Create File Handler
        self._fh_setup(formatter, log_level=log_level_file)

        # Create CLI Handler
        self._ch_setup(formatter, log_level=log_level_stream)

        # Create Event-based Handler
        self._eh_setup(formatter, log_level=log_level_event)

        # ZMQ Handler
        self._zh_setup(formatter, log_level=log_level_event)

    def _fh_setup(self, formatter, log_level=LOG_LEVEL_FILE):
        log_dir = appdirs.user_log_dir('Snout')
        Path(log_dir).mkdir(exist_ok=True, parents=True)
        log_filename = '{}.log'.format(
            arrow.now('America/New_York').format('YYYY-MM-DD'),
        )
        log_fullpath = os.sep.join([log_dir, log_filename])
        fh = logging.FileHandler(log_fullpath)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)

    def _ch_setup(self, formatter, log_level=LOG_LEVEL_STREAM):
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def _eh_setup(self, formatter, log_level=LOG_LEVEL_EVENT):
        eh = SnoutEventHandler()
        eh.setLevel(log_level)
        eh.setFormatter(formatter)
        self._logger.addHandler(eh)

    def _zh_setup(self, formatter, log_level=LOG_LEVEL_EVENT):
        zh = Logger._zh
        zh.setLevel(log_level)
        zh.setFormatter(formatter)
        # zh.setFormatter(
        #     logging.Formatter(formatter._fmt + ' (%(pathname)s, line #%(lineno)d)'), logging.DEBUG
        # )
        zh.setRootTopic(self.fullname)
        self._logger.addHandler(zh)

    @property
    def name(self):
        """Hierarchical name of the SnoutAgent object.

        Returns:
            str: Hierarchical name of the SnoutAgent object.
        """
        try:
            return self.agent.fullname
            # me = f'{self.__module__}.{self.__class__.__name__}'
            # if self._nickname:
            #     me += f'_{self._nickname}'
            # try:
            #     return '.'.join([self.parent.name, me])
        except AttributeError:
            return f'{self.__module__}.{self.__class__.__name__}'

    @property
    def fullname(self):
        """The SnoutAgent's fullname, guaranteed to be unique.

        Returns:
            str: The SnoutAgent's fullname, guaranteed to be unique.
        """
        return f'{self.name}@{hex(id(self))}'

    def debug(self, *args, **kwargs):
        return self._logger.debug(*args, *kwargs)

    def info(self, *args, **kwargs):
        return self._logger.info(*args, *kwargs)

    def warning(self, *args, **kwargs):
        return self._logger.warning(*args, *kwargs)

    def error(self, *args, **kwargs):
        return self._logger.error(*args, *kwargs)

    def exception(self, *args, **kwargs):
        return self._logger.exception(*args, *kwargs)

    def critical(self, *args, **kwargs):
        return self._logger.critical(*args, *kwargs)

    def log(self, *args, **kwargs):
        return self._logger.log(*args, *kwargs)


# Debug Wrapper
def debug(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]  # 1
        kwargs_repr = [f'{k}={v!r}' for k, v in kwargs.items()]  # 2
        signature = ', '.join(args_repr + kwargs_repr)  # 3
        Logger.logger.debug(f'Calling {func.__name__}({signature})')
        value = func(*args, **kwargs)
        Logger.logger.debug(f'{func.__name__!r} returned {value!r}')  # 4
        return value

    return wrapper_debug
