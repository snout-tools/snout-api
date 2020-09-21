import pytest

from snout.api.agent import SnoutAgent, Status


def test_classnames():
    coord1 = SnoutAgent()
    coord2 = SnoutAgent()
    assert coord1.name == coord2.name


def test_uniquenames():
    coord1 = SnoutAgent()
    coord2 = SnoutAgent()
    assert coord1.fullname != coord2.fullname


def check_snoutagent_badparent(parent):
    return SnoutAgent(parent=parent)


def test_snoutagent_parents():
    coord1 = SnoutAgent()
    coord2 = SnoutAgent(parent=coord1)
    assert coord1.parent is None
    assert coord2.parent == coord1
    with pytest.raises(TypeError):
        notcoord1 = ["I'm a list, not a coord"]
        assert check_snoutagent_badparent(notcoord1)


def test_snoutagent_children():
    coord1 = SnoutAgent()
    coord2 = SnoutAgent(parent=coord1)
    assert len(coord1.children) == 1
    assert coord1.children[0] == coord2


def test_snoutagent_transcript():
    coord = SnoutAgent()
    coord.status = Status.Starting
    coord.status = Status.Stopped
    assert len(coord.statuslog) == 3
