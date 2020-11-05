from snout.api.experiment import InstrumentAPI


def test_instrument_instance():
    i = InstrumentAPI.factory('')
    i = InstrumentAPI()
    assert i.path is None


def test_instrument_path():
    i1 = InstrumentAPI()
    assert i1.path is None
    somepath = '/usr/bin/ls'
    i2 = InstrumentAPI(path=somepath)
    assert i2.path == somepath
