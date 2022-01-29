
from typing import Union
import re

from pint.errors import DimensionalityError
from dictpy import DictSearch

from rxnpy import Quantity, Unit
from rxnpy.config.pubchem import config_PubChem
from rxnpy.config.chemical import config_chemical
from rxnpy.chemical.sub_objects.property import Prop
from rxnpy.chemical.sub_objects.condition import Cond
from rxnpy.chemical.lookup_tools.logger_lookup import logger_look_up

import unit_parse

unit_parse.config.pre_proc_sub += config_PubChem.replace_text
unit_parse.config.remove_text += config_PubChem.delete_text

config_cond = config_chemical.keys_cond


def dict_str_to_unit(dict_: dict):
    # convert unit str to Units
    for v in dict_.values():
        v["unit"] = Unit(v["unit"])


dict_str_to_unit(config_cond)

prop_unit_dict = {k[1]: k[3] for k in config_PubChem.pubchem_properties if k[3] is not None}


def get_prop(data_dict: dict) -> list[Prop]:
    """ Main function to get all properties. """
    props = []
    for p in config_PubChem.pubchem_properties:
        prop = get_prop_general(data_dict, p[0], p[1], p[2])
        if isinstance(prop, Prop):
            props.append(prop)
        elif isinstance(prop, list):
            props = props + prop

    props_cleanup(props)
    return props


def get_prop_general(data_dict: dict, search_name: str, prop_name: str, quantity_check: bool = True) \
        -> Union[None, Prop, list[Prop]]:
    """Given a property name; try to find it and clean it up."""
    result = grab_prop_from_dict(data_dict, search_name)
    if result is None:
        return None

    # do quality control
    if quantity_check and contains_number(result):
        # Clean up property data
        result = clean_property_data(result)
        if result is None or result == []:
            return None
        return conditions_check(result, prop_name)

    if isinstance(result, list) and len(result) > 1:
        return Prop(key=prop_name, value=result[0])


def grab_prop_from_dict(data_dict: dict, prop_name) -> Union[None, str, list]:
    """Try to get prop dictionary"""
    _intermediate = DictSearch(
        data=data_dict,
        target={"TOCHeading": prop_name},
        return_func=DictSearch.return_parent_object
    ).result
    if not _intermediate:  # no data
        return None

    # get values out of prop dictionary
    result = get_object(_intermediate[0][1])
    result2 = get_value(_intermediate[0][1])

    if result is None and result2 is None:
        return None
    if result is not None and result2 is None:
        return result
    if result is None and result2 is not None:
        return result2

    # result is not None and result2 is not None:
    if isinstance(result, str):
        if isinstance(result2, str):
            return [result, result2]  # str, str
        return result2.append(result)  # str, list

    if isinstance(result2, str):
        return result.append(result2)  # list, str
    return result + result2  # list, list


def get_object(data: dict, _type: str = "String") -> Union[None, str, list[str]]:
    out = DictSearch(
        data=data,
        target={_type: "*"},
        return_func=DictSearch.return_current_object
    ).result

    if not out:
        return None
    elif len(out) == 1:
        return out[0][1][_type]
    else:
        _out = []
        for i in out:
            _out.append(i[1][_type])
        return _out


def get_value(data: dict):
    out = DictSearch(
        data=data,
        target={"Number": "*"},
        return_func=DictSearch.return_parent_object
    ).result

    if not out:
        return None

    num = str(out[0][1]["Number"][0])
    if "Unit" in out[0][1]:
        unit = str(out[0][1]["Unit"])
        return num + unit

    return num


def get_prop_keys(dict_: dict) -> list[str]:
    """ From Pubchem dict, return list of properties"""
    _expt_section = DictSearch(
        data=dict_,
        target={"TOCHeading": "Experimental Properties"},
        return_func=DictSearch.return_parent_object)
    if not _expt_section.result:
        return []

    _expt_section = _expt_section.result[0][1]

    _props_list = DictSearch(
        data=_expt_section,
        target={"TOCHeading": "*"})
    return [_prop[1]["TOCHeading"] for _prop in _props_list.result]


def contains_number(obj_in: Union[str, list]) -> bool:
    """ Checks list to see if it has a number in it anywhere."""
    _pattern = r'\d'
    if isinstance(obj_in, list):
        return any([bool(re.search(_pattern, value)) for value in obj_in])
    elif isinstance(obj_in, str):
        return bool(re.search(_pattern, obj_in))
    else:
        raise TypeError


def clean_property_data(prop_list: Union[list[str], str]) -> Union[Quantity, list[Quantity], list[list[Quantity]]]:
    if isinstance(prop_list, str):
        prop_list = [prop_list]

    quantity_list = []
    for prop in prop_list:
        try:
            result = unit_parse.parser(prop)
            if result is not None:
                quantity_list.append(result)
        except:
            pass

    if len(quantity_list) == 1:
        return quantity_list[0]

    # reduce list
    return unit_parse.reduce_quantities(quantity_list)


def conditions_check(results: [Quantity, list[Quantity], list[list[Quantity]]], prop_name: str) \
        -> Union[None, Prop, list[Prop]]:
    if isinstance(results, Quantity):  # single
        return Prop(key=prop_name, value=results)

    if isinstance(results, list):
        return None

    if isinstance(results[0], Quantity):  # series
        return Prop(key=prop_name, value=results[0])

    if len(results[0]) == 1:  # condition
        return _build_prop_cond(results[0], prop_name)

    # series condition
    out = []
    for result in results:
        out.append(_build_prop_cond(result, prop_name))

    return out


def _build_prop_cond(result: list[Quantity], prop_name: str) -> Prop:
    cond_ = result[1]
    if isinstance(cond_, Quantity):
        cond_key = [k for k, v in config_cond.items() if v["unit"].dimensionality == cond_.dimensionality]
        if cond_key:  # if empty, skip condition
            cond = Cond(key=cond_key[0], value=cond_)
            return Prop(key=prop_name, value=result[0], cond=cond)

    return Prop(key=prop_name, value=result[0])


def props_cleanup(props):
    """An assortment of random methods to further clean the data."""
    for prop in props:
        if prop.key == "density":
            if isinstance(prop.value, (float, int)):
                prop.value = Quantity(f"{prop.value} g/ml")
            elif isinstance(prop.value, Quantity) and prop.value.dimensionless:
                prop.value = prop.value * Quantity(f"1 g/ml")

    # force to database units
    for prop in props:
        if prop.key in prop_unit_dict:
            try:
                prop.value = prop.value.to(prop_unit_dict[prop.key])
            except DimensionalityError:
                logger_look_up.info(f"'{prop}' can't be converted into '{prop_unit_dict[prop.key]}'.")
            except AttributeError:
                if prop_unit_dict[prop.key] == Unit(""):
                    prop.value = Quantity(prop.value)  # float that should be dimensionless
                else:
                    logger_look_up.info(f"'{prop}' can't be has no units and will be dropped.")
