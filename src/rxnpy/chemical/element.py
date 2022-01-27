import pprint

from dictpy import Serializer

from rxnpy.utilities.decorators import freeze_class


@freeze_class
class Element(Serializer):
    """


    methods
    -------
    as_dict()
        makes a JSON compatible dictionary

    """

    def __init__(self, atomic_number, name, symbol, **kwargs):
        self.atomic_number = atomic_number
        self.name = name.lower()
        self.symbol = symbol
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

    def __str__(self):
        return f"{self.atomic_number}, {self.symbol}, {self.name} + {len(self.__dict__)-4} properties"

    def __repr__(self):
        return f"{self.atomic_number}, {self.symbol}, {self.name}"

    def pprint(self):
        dict_ = self.__dict__
        dict_.pop("__frozen")
        pprint.pprint(dict_)


def local_run():
    element = Element(1, "Hydrogen", "H", phase="gas", mp=13.99)
    print(element)
    print(repr(element))
    element.pprint()
    print(element.as_dict())


if __name__ == '__main__':
    local_run()
