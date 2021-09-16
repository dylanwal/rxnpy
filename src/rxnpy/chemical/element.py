
import json


class Element:

    def __init__(self, atomic_number, name, symbol, **kwargs):
        self.atomic_number = atomic_number
        self.name = name
        self.symbol = symbol
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

    def __str__(self):
        return f"{self.atomic_number}, {self.symbol}, {self.name}"

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4, sort_keys=False)


if __name__ == '__main__':
    element = Element(1, "Hydrogen", "H", phase="gas", mp=13.99)
    print(element)
    print(repr(element))
