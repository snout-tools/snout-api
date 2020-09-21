import functools
import logging
import os
from pathlib import Path

import appdirs
import arrow

from snout.api import classproperty
from snout.api.event import EventMgmtCapability, SnoutEventHandler

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


class Logger(EventMgmtCapability):
    """Logger provides universal logging functionality to all application classes.

    Attributes:
        logger (logging.Logger): A global logger for Snout that can be used outside of class instances
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Fine tune logging setup https://docs.python.org/3/howto/logging-cookbook.html

        log_level_file = kwargs.get('log_level_file', LOG_LEVEL_FILE)
        log_level_stream = kwargs.get('log_level_file', LOG_LEVEL_STREAM)
        log_level_event = kwargs.get('log_level_ui', LOG_LEVEL_EVENT)
        try:
            self._logger = logging.getLogger(self.fullname)
        except AttributeError:
            self._logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # Create File Handler
        self._fh_setup(formatter, log_level=log_level_file)

        # Create CLI Handler
        self._ch_setup(formatter, log_level=log_level_stream)

        # Create Event-based Handler
        self._eh_setup(formatter, log_level=log_level_event)

    def _fh_setup(self, formatter, log_level=LOG_LEVEL_FILE):
        log_dir = appdirs.user_log_dir('Snout')
        Path(log_dir).mkdir(exist_ok=True, parents=True)
        log_filename = '{}.log'.format(arrow.now('America/New_York').format('YYYY-MM-DD'),)
        log_fullpath = os.sep.join([log_dir, log_filename])
        fh = logging.FileHandler(log_fullpath)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def _ch_setup(self, formatter, log_level=LOG_LEVEL_STREAM):
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def _eh_setup(self, formatter, log_level=LOG_LEVEL_EVENT):
        eh = SnoutEventHandler()
        eh.setLevel(log_level)
        eh.setFormatter(formatter)
        self.logger.addHandler(eh)

    @property
    def logger(self):
        """The logging.Logger responsible for logging this object's activity.

        Returns:
            logging.Logger: The logging.Logger responsible for logging this object's activity.
        """
        return self._logger


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
