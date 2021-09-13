
import pytest

from src.rxnpy.chemical import ChemicalFormula, ChemicalFormulaError


def test_creation():
    cf = ChemicalFormula("C1H3OH63Cr2CCCOOO")
    assert isinstance(cf, ChemicalFormula)


def test_reduce():
    cf = ChemicalFormula("C1H3OH63Cr2CCCOOO")
    assert cf.formula == "C4H66Cr2O4"


def test_reduce2():
    cf = ChemicalFormula("C1Zr")
    assert cf.formula == "CZr"


def test_reduce3():
    cf = ChemicalFormula("Zr3P4N2")
    assert cf.formula == "N2P4Zr3"


def test_reduce4():
    order = ["P", "N"]
    cf = ChemicalFormula("Zr3P4N2", order=order)
    assert cf.formula == "P4N2Zr3"


def test_invalid_element():
    with pytest.raises(ChemicalFormulaError):
        ChemicalFormula("Zc")


def test_invalid_element_order():
    with pytest.raises(ChemicalFormulaError):
        order = ["Zc", "N"]
        ChemicalFormula("Zr3P4N2", order=order)

