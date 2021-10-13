
import re

from src.rxnpy.chemical.periodic_table import PeriodicTable


class MolecularFormulaError(Exception):
    pass


class MolecularFormula:
    periodic_table = PeriodicTable()

    def __init__(self, formula, order: list[str] = None):
        """
        Chemical formula
        :param formula: chemical formula
        :param order: order of chemical symbols; defaults to hill system; or auto-completes to alphabetical by symbol
        """
        self._order = order
        self._formula = None
        self.formula = formula

        self._elements = None

    def __str__(self):
        return str(self.formula)

    def __repr__(self):
        return str(self.formula)

    @property
    def formula(self):
        return self._formula

    @formula.setter
    def formula(self, formula):
        if formula is not None:
            self._formula, self._elements = self.reduce(formula)

    def reduce(self, formula: str) -> (str, dict[str, int]):
        """
        Reduces all chemical formulas to the same reduced version.
        :param formula:
        :return:
        """
        split_formula = self._split_formula(formula)
        elements = self._split_formula_to_element_dict(split_formula)
        formula = self._element_to_formula(elements, self._order)

        return formula, elements

    @staticmethod
    def _split_formula(formula: str) -> list[str]:
        """
        Split formula up into letters and numbers.
        Example: "C1H3OH63Cr2CCCOOO" -> ['C', '1', 'H', '3', 'O', 'H', '63', 'Cr', '2', 'C', 'C', 'C', 'O', 'O', 'O']
        """
        pattern = r'[A-Z]{1}[a-z]*|\d+'
        return re.findall(pattern, formula)

    def _split_formula_to_element_dict(self, split_formula: list[str]) -> dict[str, int]:
        """
        Given a split chemical formula return a dictionary of elements.
        :param split_formula:
        :return: {"element symbol": "count"} -> {"C": 1, "O": 2}
        """
        # put data into dictionary
        elements = {}
        for index, entry in enumerate(split_formula):
            if not entry.isnumeric():
                if entry not in self.periodic_table.element_symbols:
                    raise MolecularFormulaError(f"Invalid symbol in chemical formula. Invalid: {entry}")

                if entry in elements:
                    try:
                        num_ = split_formula[index + 1]
                    except IndexError:
                        num_ = "1"
                    if num_.isnumeric():
                        elements[entry] = int(num_) + elements[entry]
                    else:
                        elements[entry] = 1 + elements[entry]
                else:
                    try:
                        num_ = split_formula[index + 1]
                    except IndexError:
                        num_ = "1"
                    if num_.isnumeric():
                        elements[entry] = int(num_)
                    else:
                        elements[entry] = 1

        return elements

    def _element_to_formula(self, elements: dict, order: list[str] = None) -> str:
        """
        Converts element dictionary into a reduced string.
        """
        # Set order
        if order is None:
            # default is hill system
            if "C" in elements.keys():
                order = self._set_element_order_in_formula(["C", "H"])
            else:
                order = self._set_element_order_in_formula()
        else:
            order = self._set_element_order_in_formula(order)

        # Generate chemical formula
        chemical_formula = ""
        for element in order:
            if element in elements.keys() and (elements[element] is not None or elements[element] == 0):
                if elements[element] == 1:
                    chemical_formula += element
                else:
                    chemical_formula += element + str(elements[element])

        return chemical_formula

    def _set_element_order_in_formula(self, order: list[str] = None) -> list[str]:
        """Given a chemical order of elements, validate it/ and complete it. Default is alphabetically."""
        base = self.periodic_table.element_symbols
        if order is None:
            return base

        for k in reversed(order):
            if k in base:
                base.remove(k)
                base.insert(0, k)
            else:
                raise MolecularFormulaError(f"Invalid symbol in 'order' for chemical formula. Invalid: {k}")

        return base


if __name__ == '__main__':
    cf = MolecularFormula("C1H3OH63Cr2CCCOOO")
    print(cf)
