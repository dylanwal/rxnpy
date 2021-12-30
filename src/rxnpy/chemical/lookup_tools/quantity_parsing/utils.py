from typing import List, Any, Optional, Union
import re

from rxnpy import Quantity


def _quantity_approx_equal(quantity1: Quantity, quantity2: Quantity, cutoff: Optional[float] = 0.02) -> bool:
    """ Returns T/F for any two quantities"""
    if not isinstance(quantity1, Quantity) or not isinstance(quantity2, Quantity):
        return False

    if quantity1.dimensionality == quantity2.dimensionality and \
            abs((quantity1 - quantity2) / quantity2) <= cutoff:
        return True

    return False


def _flatten_list(list_in: List[Any]) -> List[Any]:
    """
    Turns nested lists into a single level list.
    List[List[List[...]]]  -> List[]
    """
    if not isinstance(list_in, list):
        return list_in

    list_out = []
    for _obj in list_in:
        if isinstance(_obj, list):
            list_out += _flatten_list(_obj)
        else:
            list_out.append(_obj)

    return list_out


def _contains_number(obj_in: str) -> bool:
    """ Checks list to see if it has a number in it anywhere."""
    _pattern = r'\d'
    if isinstance(obj_in, str):
        return bool(re.search(_pattern, obj_in))
    else:
        raise TypeError