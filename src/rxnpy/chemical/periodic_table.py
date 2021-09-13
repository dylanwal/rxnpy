"""
This file contains a list of elements and a function to check chemical formulas to ensure they are reduced completely.
"""

import json

from src.rxnpy.chemical.referance_data import elements_data
from src.rxnpy.chemical.element import Element


class PeriodicTable:

    def __init__(self):
        self.elements = []
        self._load_elements()
        self.element_symbols = self.element_symbols_alphabetical_order()
        self.element_names = self.element_names_alphabetical_order()

    def __getitem__(self, atomic_number):
        return self._get_element_from_atomic_number(atomic_number)

    def _load_elements(self):
        with open(elements_data, "r", encoding="utf-8") as f:
            text = f.read()
        elements = json.loads(text)
        for k in elements:
            setattr(self, elements[k]["name"].lower(), Element(**elements[k]))
            self.elements.append(getattr(self, elements[k]["name"].lower()))

    def _get_element_from_atomic_number(self, atomic_number: int) -> Element:
        if not isinstance(atomic_number, int) or not (1 <= atomic_number <= 118):
            raise ValueError("Atomic number must be an integer between 0 - 118.")

        for element in self.elements:  # pragma: no cover
            if element.atomic_number == atomic_number:
                return element

    def element_symbols_alphabetical_order(self):
        element_symbols = [element.symbol for element in self.elements]
        return sorted(element_symbols)

    def element_names_alphabetical_order(self):
        element_names = [element.name for element in self.elements]
        return sorted(element_names)


if __name__ == '__main__':
    p_table = PeriodicTable()
    print(p_table)
    print(p_table.element_symbols_alphabetical_order())
