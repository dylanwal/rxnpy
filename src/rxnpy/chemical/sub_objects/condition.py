"""
Condition Object

"""

from dictpy import Serializer

from rxnpy.utilities.decorators import freeze_class
from rxnpy.utilities.validation import keys_check, value_check
from rxnpy.config.chemical import config_chemical
from rxnpy.chemical.sub_objects.logger import logger_chem


@freeze_class
class Cond(Serializer):
    """ Condition

    Conditions are environmental variables.

    Attributes
    ----------
    key: str
        condition key
    value: Any
        piece of information or quantity
    uncer: Any
        uncertainty in quantity

    """
    _logger = logger_chem
    keys = config_chemical.keys_cond

    def __init__(self,
                 key: str,
                 value,
                 uncer=None,
                 ):

        self._key = None
        self.key = key

        self._value = None
        self.value = value

        self._uncer = None
        self.uncer = uncer

    def __repr__(self):
        if self.uncer is None:
            return f"{self.key}: {self.value}"
        return f"{self.key}: {self.value} (+- {self.uncer})"

    @property
    def key(self):
        return self._key

    @key.setter
    @keys_check
    def key(self, key):
        self._key = key

    @property
    def value(self):
        return self._value

    @value.setter
    @value_check
    def value(self, value):
        self._value = value

    @property
    def uncer(self):
        return self._uncer

    @uncer.setter
    @value_check
    def uncer(self, uncer):
        self._uncer = uncer


def local_run():
    from rxnpy import Quantity
    cond = Cond("temp", Quantity("100 degC"), Quantity("5 degC"))
    print(cond)


if __name__ == "__main__":
    local_run()
