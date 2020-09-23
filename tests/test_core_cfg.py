import pytest

from snout.api.cfg import Config


def test_cfg_appname():
    assert isinstance(Config.appname, str)


def test_cfg_snoutfile_paths():
    default_paths = Config.snoutfile_paths()
    assert isinstance(default_paths, list)


def test_cfg_snoutfile_paths2():
    custom_paths = Config.snoutfile_paths('test')
    assert isinstance(custom_paths, list)


def test_cfg_snoutfile_paths3():
    default_paths = Config.snoutfile_paths()
    custom_paths = Config.snoutfile_paths('test')
    assert len(default_paths) + 1 == len(custom_paths)


def test_cfg_snoutfile_paths_invalidtype():
    with pytest.raises(TypeError):
        Config.snoutfile_paths(2)
