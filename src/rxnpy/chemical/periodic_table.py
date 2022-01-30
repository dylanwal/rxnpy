"""
This file contains a list of elements and a function to check chemical formulas to ensure they are reduced completely.
"""
from typing import Union
import json

from dictpy import Serializer

from rxnpy.config.quantity import Q
from rxnpy.chemical.referance_data import elements_data
from rxnpy.chemical.element import Element
from rxnpy.utilities.decorators import freeze_class

prop_conv = [
    ["atomic_mass", "g/mol"],
    ["bp", "K"],
    ["density", "g/L"],
    ["mp", "K"],
    ["molar_heat", "J/mol/K"],
    ["electron_affinity", "kJ/mol"],
    ["ionization_energies", "kJ/mol"]
]


def element_values_to_quantities(elements: dict):
    """ Adds units to element values. """
    for element in elements.values():
        for prop in prop_conv:
            if prop[0] in element and element[prop[0]] is not None:
                if isinstance(element[prop[0]], list):
                    element[prop[0]] = [Q(f"{i}, {prop[1]}") for i in element[prop[0]]]
                else:
                    element[prop[0]] = Q(f"{element[prop[0]]}, {prop[1]}")


@freeze_class
class PeriodicTable(Serializer):
    """

    attributes:
    -----------
    elements: list[Element]

    methods
    -------
    as_dict()
        makes a JSON compatible dictionary

    """

    def __init__(self):
        self.elements = []
        self._load_elements()
        self.symbols = set(self.symbols_alphabetical_order())
        self.names = set(self.names_alphabetical_order())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._get_element_by_atomic_number(key)
        elif isinstance(key, str):
            if key in self.symbols:
                return self._get_element_by_symbol(key)
            if key in self.names:
                return self._get_element_by_name(key)

    def __str__(self):
        return f"{len(self.symbols)} elements"

    def __iter__(self):
        for element in self.elements:
            yield element

    def _load_elements(self):
        with open(elements_data, "r", encoding="utf-8") as f:
            text = f.read()
        elements = json.loads(text)
        element_values_to_quantities(elements)
        for k in elements:
            setattr(self, elements[k]["name"].lower(), Element(**elements[k]))
            self.elements.append(getattr(self, elements[k]["name"].lower()))

    def _get_element_by_atomic_number(self, atomic_number: int) -> Element:
        if not isinstance(atomic_number, int) or not (1 <= atomic_number <= 118):
            raise ValueError(f"Atomic number must be an integer between 0 - 118. ({atomic_number} given)")

        for element in self.elements:  # pragma: no cover
            if element.atomic_number == atomic_number:
                return element

    def _get_element_by_symbol(self, symbol: str) -> Element:
        if not isinstance(symbol, str) or symbol not in self.symbols:
            raise ValueError(f"Invalid element symbol. ({symbol} given)")

        for element in self.elements:  # pragma: no cover
            if element.symbol == symbol:
                return element

    def _get_element_by_name(self, name: str) -> Element:
        if not isinstance(name, str) or name not in self.names:
            raise ValueError(f"Invalid element name. ({name} given)")

        name = name.lower()
        for element in self.elements:  # pragma: no cover
            if element.name == name:
                return element

    def symbols_alphabetical_order(self):
        element_symbols = [element.symbol for element in self.elements]
        return sorted(element_symbols)

    def names_alphabetical_order(self):
        element_names = [element.name for element in self.elements]
        return sorted(element_names)

    def print_table(self):
        print(generate_table(self))


periodic_table = PeriodicTable()


# Printing periodic table
structure = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10],
    [11, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 14, 15, 16, 17, 18],
    [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
    [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54],
    [55, 56, 57, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86],
    [87, 88, 89, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 0, ],
    [0, 0, 0, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 0, ]]


def generate_table(table: PeriodicTable) -> str:
    """ Returns a str of a nice periodic table. """
    # top line
    text = row_top(structure[0])
    # main body
    for i, row in enumerate(structure):
        text += row_atomic_number(row)
        text += row_symbol(row, table)
        text += row_bottom(row, row_below=structure[i+1] if i+1 < len(structure) else None)

    return text


def table_end_row(prior_col_num) -> str:
    if prior_col_num == 0:
        return "\n"
    else:
        return "|\n"


def row_top(row: list[str]) -> str:
    text = ""
    for num in row:
        if num != 0:
            text += f" _______"
        else:
            text += f"        "

    text += table_end_row(0)
    return text


def row_atomic_number(row) -> str:
    text = ""
    for i, num in enumerate(row):
        if num != 0:
            # adjust number position base on number of digits
            if num < 10:
                num = f" {num} "
            elif num < 100:
                num = f"{num} "
            text += f"|  {num}  "
        else:
            if i != 0 and row[i - 1] != 0:
                text += f"|       "
            else:
                text += f"        "

    text += table_end_row(row[-1])
    return text


def row_symbol(row: list[int], table: PeriodicTable) -> str:
    text = ""
    for i, num in enumerate(row):
        if num != 0:
            # adjust number position base on number of digits
            sym = table[num].symbol
            if len(sym) == 1:
                sym = " " + sym
            text += f"|  {sym}   "
        else:
            if i != 0 and row[i - 1] != 0:
                text += f"|       "
            else:
                text += f"        "

    text += table_end_row(row[-1])
    return text


def row_bottom(row: list[int], row_below: Union[list[int], None]) -> str:
    text = ""
    for i, num in enumerate(row):
        if num != 0:
            text += f"|_______"
        else:
            if row_below is None or row_below[i] == 0:
                if i != 0 and row[i - 1] != 0:
                    text += f"|       "
                else:
                    text += f"        "
            else:
                if i != 0 and row[i - 1] != 0:
                    text += f"|_______"
                else:
                    text += f" _______"

    text += table_end_row(row[-1])
    return text


def local_run():
    p_table = PeriodicTable()
    print(p_table)
    p_table.print_table()
    print(p_table.symbols_alphabetical_order())
    json_ = p_table.as_dict()
    print(json_)


if __name__ == '__main__':
    local_run()
