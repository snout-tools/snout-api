import logging

from snout.api.log import Logger


def test_debug():
    x = Logger()
    x.debug('debug test')


def test_info():
    x = Logger()
    x.info('info test')


def test_warning():
    x = Logger()
    x.warning('warning test')


def test_error():
    x = Logger()
    x.error('error test')


def test_critical():
    x = Logger()
    x.critical('critical test')


def test_exception():
    x = Logger()
    x.exception('exception test')


def test_log():
    x = Logger()
    x.log(logging.DEBUG, 'log test')
