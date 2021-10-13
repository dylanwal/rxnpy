from typing import List, Dict, Any, Union
from copy import deepcopy
import json
import re
from statistics import mean

from pint.errors import OffsetUnitCalculusError, UndefinedUnitError
from dictpy import DictSearch, Serializer

from src.rxnpy.chemical.molecular_formula import MolecularFormula
from src.rxnpy import Unit, Quantity

iden = [
    ["InChI", "inchi"],
    ["InChI Key", "inchi_key"],
    ["Canonical SMILES", "smiles"],
    ["Molecular Formula", "mol_formula"],
    ["CAS", "cas"]
]


prop = [
    ["Color/Form", "color"],
    ["Odor", "odor"],
    ["Boiling Point", "bp"],
    ["Melting Point", "mp"],
    ["Viscosity", "viscosity"],
    ["Vapor Pressure", "vapor_pres"],
    # ["Solubility", "solubility"],
    ["Flash Point", "flash_point"],
    ["Autoignition Temperature", "autoignition"],
    ["Heat of Combustion", "heat_combustion"],
    ["Heat of Vaporization", "heat_vaporization"],
    ["Surface Tension", "surface_tension"],
    ["Ionization Potential", "ion_potential"],
    ["Refractive Index", "refract_index"]
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
            setattr(self, p[1], self.get_prop(p[0]))

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


    def reduce_duplicates(self, result: List) -> Any:
        """Find most repeated value."""
        result_set = list(set(result))
        counts = [result.count(value) for value in result_set]
        return result_set[counts.index(max(counts))]

    def get_prop(self, prop_name: str):
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

        if self._contains_number(result):
            result = result if isinstance(result, list) else [result]
            result = self._process_numerical_data(result)

        return result

    @staticmethod
    def _contains_number(data: List) -> bool:
        """ Checks list to see if it has a number in it anywhere."""
        return any([bool(re.search(r'\d', value)) for value in data])

    def _process_numerical_data(self, result: List[str]) -> Union[Quantity, List[List[Quantity]]]:
        """
        Takes a list of strings figures out the quanity to return.
        Or if conditions are found it return List[value, condition]
        If multiple conditions found List[List[value, condition]]

        :param result: List of strings that contain property data
        :return:
        """
        cleaned_data = []
        for data in result:
            # genernal data cleaning
            data = re.sub("[\(].*[\)]", "", data)
            data = re.sub("^[a-zA-Z;,.: /]*", "", data)
            data = re.sub("@", "at", data)
            data = re.sub("={1}.*$", "", data)

            # look for "### unit at ### unit"
            # if we find this list, take all the data
            if len(data_found :=
                   re.findall("[-.0-9]{1,7} {0,1}[^0-9,/;]{0,8} at [-.0-9]{1,7} {0,1}[^0-9,/;]{0,8}", data)) >= 1:
                out = []
                for point in data_found:
                    points = re.findall("[-.0-9]{1,6}[ ]{0,2}[^0-9,/]{0,8}", point)
                    main_value = self._make_quanity(re.sub("at", "", points[0]))
                    cond = self._make_quanity(points[1])
                    if main_value is not None and cond is not None: out.append([main_value, cond])

                return out

            # reduce ranges
            if bool(data_found :=re.findall("([-.0-9]{1,6}[- ]{1,3}[-.0-9]{1,6})|([-.0-9]{1,6}[^0-9-,/;]{0,8}[- ]{1,"
                                     "3}[-.0-9]{1,6}[^0-9,/;]{0,8})",data)):
                data = re.findall("[-.0-9]{1,6}[^0-9-,/; ]{0,8}", data_found)[0]

            # convert to quanity
            data = self._make_quanity(data)
            if data is not None: cleaned_data.append(data)

        # Narrow down list
        return self._reduce_unit_list(cleaned_data)

    @staticmethod
    def _make_quanity(text: str) -> Quantity:
        value = re.findall('^[0-9.-]+', text.lstrip())[0]
        unit = text.strip(value).replace(" ", "")

        unit = re.sub("LB", "lb", unit)
        find_dash = re.search("[^0-9]{1}-{1}[^0-9]{1}", unit)
        if find_dash is not None:
            unit = unit[:find_dash.span()[0]+1] + "*" + unit[find_dash.span()[1]-1:]

        try:
            try:
                return float(value) * Unit(unit)
            except OffsetUnitCalculusError:
                if re.findall('F', text):
                    return float(value) * Unit("degF")
                elif re.findall("C", text):
                    return float(value) * Unit("degC")
        except UndefinedUnitError:
            pass

        return None

    @staticmethod
    def _reduce_unit_list(data_in: List[Quantity]) -> Quantity:
        if len(data_in) <= 2:
            return data_in[0]

        # find most common dimnsion and filter out any bad ones.
        unit_dimnsionality_count = {}
        for data in data_in:
            if data.dimensionality not in unit_dimnsionality_count:
                unit_dimnsionality_count[data.dimensionality] = 1
            else:
                unit_dimnsionality_count[data.dimensionality] += 1

        most_common_unit = max(unit_dimnsionality_count, key=unit_dimnsionality_count.get)
        data_in = [data for data in data_in if most_common_unit == data.dimensionality]

        # remove data furthest from average till 1 point left
        for i in range(len(data_in)-1):
            data_average = sum([data.to_base_units() for data in data_in])/len(data_in)
            differance_list = [abs(data.to_base_units()-data_average) for data in data_in]
            data_in.pop(differance_list.index(max(differance_list)))

        return data_in[0]

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

        if self.mol_formula:
            self.mol_formula = MolecularFormula(self.mol_formula)


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
        with open(file_path, "r", encoding="UTF-8") as f:
            text = f.read()
            json_data = json.loads(text)

        return json_data


    # load in json files
    json_data = []
    for file in files_list:
        json_data.append(get_data(file))

    # run extration on json files
    materials = []
    for data in json_data[0:1]:
        material = PubChemMaterial(data)
        print(material)
        materials.append(material)

    print("done")