from snout.api.log import Logger


class AClass(Logger):
    def __init__(self):
        super().__init__()


def test_local_logger():
    a = AClass()
    assert a.logger


def test_global_logger():
    assert AClass.logger
