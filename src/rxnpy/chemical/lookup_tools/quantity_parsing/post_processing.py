from typing import List

from rxnpy import Quantity
from rxnpy.chemical.lookup_tools.quantity_parsing.utils import _quantity_approx_equal


def _remove_duplicates(list_quantities: List[Quantity]) -> List[Quantity]:
    """Remove quantities if the are the same. (can be different units, same dimensionality, and approximately same)"""
    if not isinstance(list_quantities, list) or len(list_quantities) <= 1:
        return list_quantities

    if isinstance(list_quantities[0], list):
        new_list_quantities = []
        for sublist in list_quantities:
            new_list_quantities.append(_duplicate_check(sublist))
    else:
        new_list_quantities = _duplicate_check(list_quantities)

    return new_list_quantities


def _duplicate_check(list_quantities: List[Quantity]) -> List[Quantity]:
    if len(list_quantities) % 2 == 0:
        new_list_quantities = []
        for i in range(int(len(list_quantities)/2)):
            pair = list_quantities[i*2: i*2+2]
            if _quantity_approx_equal(pair[0], pair[1]):
                new_list_quantities.append(pair[0])  # approximate same
            else:
                new_list_quantities.append(pair[0])  # different quantities
                new_list_quantities.append(pair[1])

        list_quantities = new_list_quantities

    return list_quantities


if __name__ == "__main__":
    from testing_utils import _test_func

    test_remove_duplicates = [  # [Input, Output]
        # positive control (changes)
        [[Quantity("40 degF"), Quantity("4 degC")], [Quantity("40 degF")]],
        [[Quantity("40 degF"), Quantity("4 degC"), Quantity("32 degF"), Quantity("0 degC")], [Quantity("40 degF"), Quantity("32 degF")]],

        # negative control (no changes)
        [[Quantity("40 degF")], [Quantity("40 degF")]],
        [Quantity("40 degF"), Quantity("40 degF")],
        [[Quantity("40 degF"), Quantity("20 kPa")], [Quantity("40 degF"), Quantity("20 kPa")]],
        [[Quantity("40 degF"), Quantity("4 degF")], [Quantity("40 degF"), Quantity("4 degF")]],

    ]
    _test_func(_remove_duplicates, test_remove_duplicates)
