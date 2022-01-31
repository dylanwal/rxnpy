"""
Property Object
"""
from typing import Union

from dictpy import Serializer

from rxnpy.utilities.decorators import freeze_class
from rxnpy.utilities.reference_list import ObjList
from rxnpy.config.quantity import Quantity
from rxnpy.chemical.sub_objects.condition import Cond
from rxnpy.chemical.sub_objects.logger import logger_chem


class PropError(Exception):
    pass


@freeze_class
class Prop(Serializer):
    """ Properties

    Properties are qualities or traits that belonging to a node.

    Attributes
    ----------
    key: str (has keys)
        type of property
    value: Any
        piece of information or quantity
    uncer: Any
        uncertainty in quantity
    method: str
        approach or source of property data
    cond: list[Cond]
        conditions that the property was taken under

    """
    _logger = logger_chem

    def __init__(
            self,
            key: str,
            value,
            uncer=None,
            method: str = None,
            cond: Union[Cond, list[Cond]] = None,
    ):

        self._key = None
        self.key = key

        self._value = None
        self.value = value

        self._uncer = None
        self.uncer = uncer

        self._method = None
        self.method = method

        self._cond = ObjList(Cond, cond, self._logger)

    def __repr__(self):
        text = ""
        text += f"{self.key}: {self.value}"
        if self.uncer is not None:
            text += f"(+- {self.uncer})"
        if len(self.cond) > 0:
            text += f" [{self.cond}]"
        return text

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def uncer(self):
        return self._uncer

    @uncer.setter
    def uncer(self, uncer):
        self._uncer = uncer

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method

    @property
    def cond(self):
        return self._cond

    @cond.setter
    def cond(self, _):
        raise AttributeError("Use '.add()' or .remove() to modify.")

    @staticmethod
    def load(dict_: dict):
        if "cond" in dict_:
            cond = dict_.pop("cond")
        else:
            cond = None

        if "value" in dict_:
            try:
                dict_["value"] = Quantity(dict_["value"])
            except Exception:
                pass

        prop = Prop(**dict_)

        if cond:
            for con in cond:
                prop.cond.add(Cond.load(con))

        return prop


def local_run():
    from rxnpy import Quantity
    prop = Prop("bp", Quantity("100 degC"), method="simulation", cond=Cond("pres", Quantity("2 atm")))
    prop.cond.add(Cond("temp", Quantity("2 degC")))
    prop.cond.add(Cond("temp", Quantity("2 degC")))
    prop.cond.add(Cond("temp", Quantity("2 degC")))
    print(prop)


if __name__ == '__main__':
    local_run()
