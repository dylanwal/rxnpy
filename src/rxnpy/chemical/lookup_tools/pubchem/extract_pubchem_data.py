from typing import List, Dict, Any, Union
import json
import re

from dictpy import DictSearch, Serializer
from rxnpy.chemical.lookup_tools.quantity_parsing import main_quantity_parse, reduce_quantity_list

from rxnpy.chemical.molecular_formula import MolecularFormula
from rxnpy import Quantity

iden = [
    ["InChI", "inchi"],
    ["InChI Key", "inchi_key"],
    ["Canonical SMILES", "smiles"],
    ["Molecular Formula", "mol_formula"],
    ["CAS", "cas"]
]


prop = [
    ["Color/Form", "color", False],
    ["Odor", "odor", False],
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


class PubChemMaterial(Serializer):

    def __init__(self, data: Dict):
        """
        Takes the JSON from PubChem and generates a class of properties.

        :param data: Dictionary of JSON from PubChem
        """
        self.data = data

        self.pubchem_cid = self.get_cid()
        self.name = self.get_name()
        self.names = self.get_names()

        for i in iden:
            setattr(self, i[1], self.get_iden(i[0]))

        for p in prop:
            setattr(self, p[1], self.get_prop(p[0], p[2]))

        self.post_processing()

    def __str__(self):
        dict_out = self.remove_none(self.dict_cleanup(self.as_dict()))
        dict_out.pop("data")
        return json.dumps(dict_out, indent=2, sort_keys=False)

    def get_iden(self, iden_name: str):
        try:
            _intermediate = DictSearch(
                data=self.data,
                target={"TOCHeading": iden_name},
                return_func=DictSearch.return_parent_object
            ).result[0][1]
            result = self.get_object(_intermediate)
        except IndexError:
            return None

        if isinstance(result, list):
            result = self.reduce_duplicates(result)

        return result

    @staticmethod
    def reduce_duplicates(result: List) -> Any:
        """Find most repeated value."""
        result_set = list(set(result))
        counts = [result.count(value) for value in result_set]
        return result_set[counts.index(max(counts))]

    def get_prop(self, prop_name: str, numerical: bool = True):
        """Given a property name; try to find it and clean it up."""
        try:
            _intermediate = DictSearch(
                data=self.data,
                target={"TOCHeading": prop_name},
                return_func=DictSearch.return_parent_object
            ).result[0][1]
            result = self.get_object(_intermediate)
        except IndexError:
            return None

        if numerical and self._contains_number(result):
            result = result if isinstance(result, list) else [result]
            result = self._process_numerical_data(result)
        else:
            if isinstance(result, list) and len(result) > 1:
                result = result[0]

        return result

    @staticmethod
    def _contains_number(obj_in: Union[str, List]) -> bool:
        """ Checks list to see if it has a number in it anywhere."""
        _pattern = r'\d'
        if isinstance(obj_in, list):
            return any([bool(re.search(_pattern, value)) for value in obj_in])
        elif isinstance(obj_in, str):
            return bool(re.search(_pattern, obj_in))
        else:
            raise TypeError

    @staticmethod
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

    def get_cid(self) -> int:
        return int(DictSearch(
            data=self.data,
            target={"RecordNumber": "*"},
            return_func=DictSearch.return_current_object
        ).result[0][1]["RecordNumber"])

    def get_name(self) -> str:
        return str(DictSearch(
            data=self.data,
            target={"RecordTitle": "*"},
            return_func=DictSearch.return_current_object
        ).result[0][1]["RecordTitle"])

    def get_names(self) -> str:
        _intermediate = DictSearch(
            data=self.data,
            target={"TOCHeading": "Depositor-Supplied Synonyms"},
            return_func=DictSearch.return_parent_object
        ).result[0][1]
        return self.get_object(_intermediate)[:5]

    def post_processing(self):
        """An assortment of random methods to further clean the data."""
        if self.inchi:
            self.inchi = self.inchi.strip("InChI=")

        if self.names:
            pattern = r"([0-9]+[-]{1}[0-9]+[-]{1}[0-9]+)|([0-9]{3})"
            self.names = [name for name in self.names if not re.search(pattern, name)]
            
            if self.name not in self.names:
                self.names.append(self.name)

        if self.mol_formula:
            self.mol_formula = MolecularFormula(self.mol_formula)

    @staticmethod
    def _process_numerical_data(result: List[str]) -> Union[Quantity, List[List[Quantity]]]:
        """
        Takes a list of strings figures out the quanity to return.
        Or if conditions are found it return List[value, condition]
        If multiple conditions found List[List[value, condition]]

        :param result: List of strings that contain property data
        :return:
        """
        out = []
        for r in result:
            q = main_quantity_parse(r)
            if q != [] and q is not None:
                out.append(q)

        out = reduce_quantity_list(out)
        return out


if __name__ == "__main__":
    import glob
    import os
    from pathlib import Path

    # Find all json files
    files_list = []
    path = (Path(__file__).parent / Path("data"))
    os.chdir(path)
    for files in glob.glob("cid_*.json"):
        files_list.append(files)  # filename with extension


    def get_data(file_path: Path) -> dict:
        with open(file_path, "r", encoding="latin-1") as f:
            text = f.read()
            json_data = json.loads(text)

        return json_data


    # load in json files
    json_data = []
    for file in files_list:
        json_data.append(get_data(file))

    # run extraction on json files
    materials = []
    for _data in json_data:
        material = PubChemMaterial(_data)
        print(material)
        materials.append(material)

    print("done")
