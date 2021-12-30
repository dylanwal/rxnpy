from typing import Dict, List
import json

from dictpy import DictSearch

from rxnpy.chemical.lookup_tools.quantity_parsing.utils import _flatten_list


prop = [
    ["Stability/Shelf Life", "s", False],
    ["Decomposition", "d", False],
    ["Kovats Retention Index", "k", True],
    ["Odor Threshold", "o", True],
    ["Density", "density", True],
    ["Boiling Point", "bp", True],
    ["Melting Point", "mp", True],
    ["Viscosity", "viscosity", True],
    ["Vapor Pressure", "vapor_pres", True],
    ["Vapor Density", "vapor_density", True],
    ["Flash Point", "flash_point", True],
    ["Autoignition Temperature", "autoignition", True],
    ["Heat of Combustion", "heat_combustion", True],
    ["Heat of Vaporization", "heat_vaporization", True],
    ["Surface Tension", "surface_tension", True],
    ["Refractive Index", "refract_index", True],
    ["LogP", "log_p", True],
    ["pKa", "pka", True],
    ["pH", 'ph', True],
    ["Henrys Law Constant", "henry_constant", True],
    ["Optical Rotation", "optical_rot", True]
]


def get_prop_list_data(_dict: Dict) -> List[str]:
    out = []
    for p in prop:
        result = get_prop(_dict, p[0])
        if result is not None:
            out.append(result)

    return _flatten_list(out)


def get_prop(_dict, prop_name: str):
    """Given a property name; try to find it and clean it up."""
    try:
        _intermediate = DictSearch(
            data=_dict,
            target={"TOCHeading": prop_name},
            return_func=DictSearch.return_parent_object
        ).result[0][1]
        result = get_object(_intermediate)
    except IndexError:
        return None

    return result


def get_object(data: dict, _type: str = "String"):
    out = DictSearch(
        data=data,
        target={_type: "*"},
        return_func=DictSearch.return_current_object
    ).result
    if len(out) == 1:
        return out[0][1][_type]
    else:
        _out = []
        for i in out:
            _out.append(i[1][_type])
        return _out

if __name__ == "__main__":
    import glob
    import os
    from pathlib import Path

    # Find all json files
    files_list = []
    path = (Path(__file__).parent / Path("data"))
    os.chdir(r"C:\Users\nicep\Desktop\pubchem\json_files")
    k = 0
    for files in glob.glob("cid_*.json"):
        files_list.append(files)  # filename with extension
        k += 1
        if k == 50:
            break

    def get_data(file_path: Path) -> dict:
        with open(file_path, "r", encoding="UTF-8") as f:
            _text = f.read()
            _json_data = json.loads(_text)

        return _json_data


    # load in json files
    json_data = []
    for file in files_list:
        json_data.append(get_data(file))

    # run extraction on json files
    props_list = []
    for _data in json_data:
        props_list += get_prop_list_data(_data)

    for p in props_list:
        print(p)
    print("done")
