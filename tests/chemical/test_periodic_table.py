
import pytest

from rxnpy.chemical import PeriodicTable, Element


@pytest.fixture
def table():
    return PeriodicTable()


def test_creation(table):
    assert isinstance(table, PeriodicTable)


def test_scriptable(table):
    assert isinstance(table[1], Element)


def test_scriptable_invalid(table):
    with pytest.raises(ValueError):
        a = table[200]


def test_name(table):
    assert isinstance(table.hydrogen, Element)


def test_element_symbols(table):
    assert table.element_symbols is not None
    assert table.element_symbols == sorted(table.element_symbols)


def test_element_names(table):
    assert table.element_names is not None
    assert table.element_names == sorted(table.element_names)
