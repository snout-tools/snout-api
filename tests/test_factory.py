import snout.api.factory

MAIN = 'apitest'
VARIANT = 'fancy'


def test_factory_properties():
    f = snout.api.factory.Factory(MAIN)
    assert isinstance(snout.api.factory.Factory._plugins, dict) and not bool(
        snout.api.factory.Factory._plugins
    )
    p = f.plugins()
    assert isinstance(p, dict) and bool(p)
    assert isinstance(snout.api.factory.Factory._plugins, dict) and bool(
        snout.api.factory.Factory._plugins
    )
    assert f.main == MAIN
    assert f.variant is None
    f2 = snout.api.factory.Factory(MAIN, VARIANT)
    assert f2.variant == VARIANT


def test_factory_list():
    f = snout.api.factory.Factory(MAIN)
    ls = f.ls(ret=True)
    assert isinstance(ls, str)
    assert 'apitest' in ls
    ls2 = f.ls()
    assert isinstance(ls2, type(None))


def test_factory_instance():
    f = snout.api.factory.Factory(MAIN)
    i = f.instance()
    f2 = i(MAIN)
    assert isinstance(f2, snout.api.factory.Factory)
    i = f.instance('fancy')
    f2 = i(MAIN)
    assert isinstance(f2, snout.api.factory.Factory)
