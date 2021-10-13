
import pytest

from rxnpy.chemical import MolecularFormula, MolecularFormulaError


def test_creation():
    cf = MolecularFormula("C1H3OH63Cr2CCCOOO")
    assert isinstance(cf, MolecularFormula)


def test_reduce():
    cf = MolecularFormula("C1H3OH63Cr2CCCOOO")
    assert cf.formula == "C4H66Cr2O4"


def test_reduce2():
    cf = MolecularFormula("C1Zr")
    assert cf.formula == "CZr"


def test_reduce3():
    cf = MolecularFormula("Zr3P4N2")
    assert cf.formula == "N2P4Zr3"


def test_reduce4():
    order = ["P", "N"]
    cf = MolecularFormula("Zr3P4N2", order=order)
    assert cf.formula == "P4N2Zr3"


def test_invalid_element():
    with pytest.raises(MolecularFormulaError):
        MolecularFormula("Zc")


def test_invalid_element_order():
    with pytest.raises(MolecularFormulaError):
        order = ["Zc", "N"]
        MolecularFormula("Zr3P4N2", order=order)

