import logging
from typing import Protocol, Any, Union
from types import GenericAlias
from functools import wraps
from difflib import get_close_matches

from pint.errors import DimensionalityError

from rxnpy import Quantity


class SupportsKeyCheck(Protocol):
    _logger: logging.Logger = None
    keys: dict = None
    key: str = None
    value: Any = None


class TempClass:
    keys = None

    def __init__(self, keys):
        self.keys = keys


def keys_check(args):
    """ Key checks

    Checks to see if keyword is in official keyword list, or the key has a 'plus' or '+' at the beginning.

    Parameters
    ----------
    args: Callable or dict
        function or key table

    """
    keys = None

    def keys_check_decorator(func):
        @wraps(func)
        def _key_check(self, key):
            if key is not None:
                if keys is not None:
                    self = keys
                do_key_check(self, key)
            return func(self, key)

        return _key_check

    if callable(args):
        return keys_check_decorator(args)

    keys = TempClass(args)
    return keys_check_decorator


def do_key_check(self: SupportsKeyCheck, key: Union[list[str], str]):
    """
    Parameters
    ----------
    self: SupportsKeyCheck
        class that key is being added to
    key: str
        key to be checked
    """
    if isinstance(key, list):
        for k in key:
            do_key_check(self, k)  # recursion!
    elif isinstance(key, str):
        if key in self.keys or key.startswith(("plus", "+")):
            return
        else:
            mes = f" {key} is not a official keyword.\n" \
                  f"Did you mean: {key_recommendation(key, list(self.keys.keys()))}\n" \
                  "Otherwise add a '+' (plus symbol) in front of your key to signify a custom condition."
            raise ValueError(mes)
    else:
        raise TypeError(f"The 'key/keyword' for CRIPT must be string. Invalid: {key} ({type(key)})")


def value_check(func):
    """ value checks

    Checks to see if value matches units of key

    """
    @wraps(func)
    def _value_check(self: SupportsKeyCheck, value):
        if value is not None:
            do_value_check(self, value)
        value = func(self, value)
        return value

    return _value_check


def do_value_check(self: SupportsKeyCheck, value):
    """
    """
    # guard statements
    if self.key is None:
        mes = f"'key' needs to be defined first."
        self._logger.error(mes)
        raise

    if self.key.startswith(("plus", "+")):
        return  # no checks on custom condition

    type_ = self.keys[self.key]["type"]

    if hasattr(type_, "class_"):
        type_ = (type_, dict)

    if isinstance(type_, GenericAlias):
        _value_check_generic(self, value)
        return

    if not isinstance(value, type_):
        mes = f"Invalid 'value' type provided for {self.key}. Expected: {type_}; Received: {type(value)}"
        self._logger.error(mes)
        raise

    # Does other type specific checks
    if type_ == str:
        _value_str_check(self, value)
    elif type_ == float or type_ == int:
        _value_num_check(self, value)
    elif type_ == Quantity:
        _value_quantity_check(self, value)
    else:
        pass  # other types have no checks


def _value_str_check(self, value: str):
    """ Checks value of strings. """
    range_ = self.key.key_dict["range"]

    if not range_:  # no range check
        return
    elif isinstance(range_[0], int) and range_[0] <= len(value) <= range_[1]:  # text length check
        return
    elif isinstance(range_[0], str) and value in range_:  # multiple string options
        return
    else:
        mes = f"'Value' outside expected range for {self.key}. Expected: {range_}; Received: {value}"
        self._logger.error(mes)
        raise


def _value_num_check(self, value: Union[int, float]):
    """ Checks value of numbers. """
    range_ = self.key.key_dict["range"]

    if range_[0] <= value <= range_[1]:
        return
    else:
        mes = f"'Value' outside expected range for {self.key}. Expected: {range_}; Received: {value}"
        self._logger.error(mes)
        raise


def _value_quantity_check(self, value: Quantity):
    """ Checks value of quantities. """
    range_ = self.keys[self.key]["range"]
    unit_ = self.keys[self.key]["unit"]

    # Check units
    try:
        new_arg = value.to(unit_)  # Unit Conversion
    except DimensionalityError:
        mes = f"Wrong units provided for {self.key}. Expected: {unit_} or similar dimensionality; " \
              f"Received: {value.units}"
        self._logger.error(mes)
        raise

    # Check range
    if range_[0] <= new_arg.magnitude <= range_[1]:
        return
    else:
        mes = f"'Value' outside expected range for {self.key}. Expected: {range_}; Received: {value}"
        self._logger.error(mes)
        raise


def _value_check_generic(self, value: Union[list, tuple]):
    """ Handles GenericAlias types. Which means its a list or tuple of something."""

    # do type check
    type_ = self.key.key_dict["type"]
    split_type = [type_.__origin__, type_.__args__[0]]  # convert generic to real types

    if not isinstance(value, split_type[0]) and not all(isinstance(v, split_type[1]) for v in value):
        mes = f"Invalid 'value' type provided for {self.key}. Expected: {type_}; Received: {type(value)}"
        self._logger.error(mes)
        raise

    # do range and unit checks
    for v in value:
        if isinstance(v, str):
            _value_str_check(self, v)
        elif isinstance(v, int):
            _value_num_check(self, v)
        elif isinstance(v, Quantity):
            _value_quantity_check(self, v)


def key_recommendation(guess: str, possibilities: list) -> str:
    """ Given a bad key suggest nearest options. """
    best_guess = get_close_matches(guess, possibilities, cutoff=0.4, n=3)
    if best_guess is []:
        return ""

    return ", ".join(best_guess)
