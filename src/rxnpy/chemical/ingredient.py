from enum import Enum, auto
from functools import total_ordering
from dataclasses import dataclass
import json

from dictpy import Serializer

from rxnpy import Quantity, Unit, float_limit


class IngredientError(Exception):
    pass


Qty = {
    "mass": {
        "range": [0, float_limit],
        "unit": "g",
    },
    "volume": {
        "range": [0, float_limit],
        "unit": "ml"
    },
    "pressure": {
        "range": [0, float_limit],
        "unit": "kPa",
    },
    "mole": {
        "range": [0, float_limit],
        "unit": "mmole",
    },
    "equivalence": {
        "range": [0, float_limit],
        "unit": "",
    },
    "molarity": {
        "range": [0, float_limit],
        "unit": "M",
    },
    "mass_fraction": {
        "range": [0, 1],
        "unit": ""
    },
    "molar_concentration": {
        "range": [0, float_limit],
        "unit": "M"
    },
    "molar_mass": {
        "range": [0, float_limit],
        "unit": "g/mol"
    },
    "density": {
        "range": [0, float_limit],
        "unit": "g/ml"
    }
}


@total_ordering
class IngrRole(Enum):
    """
    Order is used for choosing 'base' for relative quantities.
    First listed is will be given priority for becoming the base.
    """
    INITIATOR = auto()
    CTA = auto()
    CATALYST = auto()

    SUBSTRATE = auto()
    REAGENT = auto()
    MONOMER = auto()
    POLYMER = auto()

    SOLVENT = auto()
    INERT = auto()

    WORKUP = auto()
    QUENCH = auto()

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


@dataclass
class Ingredient(Serializer):
    name: str
    mass: Quantity = None
    volume: Quantity = None
    pressure: Quantity = None
    mole: Quantity = None

    equivalence: Quantity = None
    molarity: Quantity = None
    mass_fraction: Quantity = None

    density: Quantity = None
    molar_mass: Quantity = None
    molar_concentration: Quantity = None

    keyword: IngrRole = None

    def __str__(self):
        return f"{self.name},{' (' + str(self.keyword) + ')' if self.keyword is not None else ''}"

    def __repr__(self):
        return json.dumps(self.as_dict(remove_none=True), indent=4, sort_keys=False)

    def __post_init__(self):
        for key in Qty.keys():
            self._unit_and_range_check(key)

    def _unit_and_range_check(self, key: str):
        """ Checks to make sure value is in the acceptable range."""
        if (qty := getattr(self, key)) is None:
            return

        range_ = Qty[key]["range"]
        unit_ = Qty[key]["unit"]
        self._unit_check(qty, Unit(unit_), key)
        if range_[0] <= qty.to(unit_).magnitude <= range_[1]:
            return
        else:
            mes = f"{key} outside valid range. Valid range: {range_} {unit_}; Received: {qty.to(unit_)} ({qty})"
            raise IngredientError(mes)

    @staticmethod
    def _unit_check(value: Quantity, expected: Unit, name: str):
        """ Checks to make sure unit dimensionality is correct"""
        if value.dimensionality != expected.dimensionality:
            mes = f"Invalid {name} dimensionality. Expected: {expected.dimensionality}, " \
                  f"Received: {value.dimensionality}."
            raise IngredientError(mes)


if __name__ == "__main__":
    ingr = Ingredient(**{
        "name": "secbuLi",
        "volume": 0.0172 * Unit("ml"),
        "molar_mass": 64.06 * Unit("g/mol"),
        "density": 0.768 * Unit("g/ml"),
        "molar_concentration": 1.3 * Unit("M"),
        "keyword": IngrRole.INITIATOR
    })
    print(ingr)
    print(repr(ingr))
