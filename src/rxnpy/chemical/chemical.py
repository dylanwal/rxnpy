
import json


from molecular_formula import MolecularFormula
from ingredient import Ingredient


class Chemical(Ingredient):

    def __init__(self,
                 formula: str = None,
                 **kwargs):

        self._formula_obj = MolecularFormula(None, kwargs.pop("order") if "order" in kwargs.keys() else None)
        self._formula = None
        self.formula = formula

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        list_ = ["name", "formula"]
        return ", ".join([getattr(self, v) for v in list_ if getattr(self, v) is not None])

    def __repr__(self):
        skip = ["_formula_obj"]
        return json.dumps(self.as_dict(skip=skip), indent=4, sort_keys=False)

    @property
    def formula(self):
        return self._formula

    @formula.setter
    def formula(self, formula):
        self._formula_obj.formula = formula
        self._formula = self._formula_obj.formula


if __name__ == "__main__":
    from pint import Unit
    from ingredient import IngrRole
    chemical = Chemical(**{
        "name": "secbuLi",
        "formula": "C3H7Li",
        "volume": 0.0172 * Unit("ml"),
        "molar_mass": 64.06 * Unit("g/mol"),
        "density": 0.768 * Unit("g/ml"),
        "molar_concentration": 1.3 * Unit("M"),
        "keyword": IngrRole.INITIATOR,
        "bp": 100,
        "cas": "3432-23432-23"
    })
    print(chemical)
    print(repr(chemical))
