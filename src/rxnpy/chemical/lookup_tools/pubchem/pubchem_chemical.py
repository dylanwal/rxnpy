from typing import Any, Union
import json
import re
import time
import urllib.request
import pprint

from dictpy import DictSearch, Serializer
import unit_parse

from rxnpy import Quantity
from rxnpy.config.pubchem import config_PubChem
from rxnpy.chemical.lookup_tools.logger_lookup import logger_chem_look_up
from rxnpy.chemical.sub_objects.molecular_formula import MolecularFormula
from rxnpy.chemical.utils import calc_molar_mass


unit_parse.config.pre_proc_sub += config_PubChem.replace_text
unit_parse.config.remove_text += config_PubChem.delete_text


class AttList(Serializer):

    def __init__(self):
        pass

    def add(self, name, obj):
        setattr(self, name, obj)

    def __iter__(self):
        attr = vars(self)
        return attr.items()


class PubChemChemical(Serializer):
    """ PubChemMaterial

    Gets data from PubChem and cleans it.

    Attributes
    ----------
    raw_data: dict
        dictionary of JSON from PubChem
    iden: AttList
        chemical identifiers
    prop: AttList
        chemical properties

    """
    config_iden = config_PubChem.pubchem_identities
    config_prop = config_PubChem.pubchem_properties

    def __init__(self, cid: int = None, raw_data: dict = None):
        """ __init__

        Parameters
        ----------
        cid: int
            PubChem CID
        raw_data: dict
            JSON from PubChem
        """
        # if cid provided go get data from website
        if cid:
            raw_data = self.download_from_pubchem(cid)
        self.raw_data = raw_data

        # get chemical identifiers
        self.iden = AttList()
        self.get_iden()

        # get chemical properties
        self.prop = AttList()
        self.get_prop()

        self.post_processing()
        logger_chem_look_up.debug(f"PubChem: cid_{self.iden.pubchem_cid} finish obtaining identifiers and properties.")

    def __str__(self):
        return f"{self.iden.name} (cid {self.iden.pubchem_cid})"

    def pprint(self):
        dict_out = self.remove_none(self.dict_cleanup(self.as_dict()))
        dict_out.pop("raw_data")
        return pprint.pprint(dict_out)

    @staticmethod
    def download_from_pubchem(cid: int) -> dict:
        """

        Download data from Pubchem.

        Parameters
        ----------
        cid: int

        Returns
        -------
        Pubchem JSON: dict

        """
        logger_chem_look_up.debug(f"PubChem: cid_{cid} attempting to download.")
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
        flag = True
        ii = 0
        while flag:
            try:
                # do web request
                with urllib.request.urlopen(url) as url_data:
                    # load data into a dictionary
                    json_data = json.loads(url_data.read().decode("UTF-8"))
                logger_chem_look_up.debug(f"PubChem: cid_{cid} downloaded.")
                return json_data

            except Exception as e:  # if web request fails
                # pause to avoid triggering 'denial-of-service' error
                time.sleep(5)
                ii += 1
                if ii == 5:  # stop completely if it can't get the JSON
                    logger_chem_look_up.error(f"PubChem: download of cid_{cid} failed due to too many failed tries.")
                    raise RuntimeError(e)

    # Identity stuff
    ##################################################################################################################
    def get_iden(self):
        self.iden.add("pubchem_cid", self._get_cid())
        logger_chem_look_up.debug(f"PubChem: cid_{self.iden.pubchem_cid} starting to parse identifiers and properties.")
        self.iden.add("name", self._get_name())
        self.iden.add("names", self._get_names())
        for i in self.config_iden:
            self.iden.add(i[1], self._get_iden_general(i[0]))

    def _get_cid(self) -> int:
        return int(DictSearch(
            data=self.raw_data,
            target={"RecordNumber": "*"},
            return_func=DictSearch.return_current_object
        ).result[0][1]["RecordNumber"])

    def _get_name(self) -> str:
        """ Get chemical name. """
        return str(
            DictSearch(data=self.raw_data, target={"RecordTitle": "*"},
                       return_func=DictSearch.return_current_object).result[0][1]["RecordTitle"]
        )

    def _get_names(self) -> Union[list[str], None]:
        """ Get chemical names. """
        _intermediate = DictSearch(data=self.raw_data, target={"TOCHeading": "Depositor-Supplied Synonyms"},
                                   return_func=DictSearch.return_parent_object).result
        if not _intermediate:  # section not present
            return None

        result = self.get_object(_intermediate[0][1])
        if isinstance(result, str):
            return [result]

        return result[:8]

    @staticmethod
    def get_object(data: dict, _type: str = "String"):
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

    def _get_iden_general(self, iden_name: str):
        _intermediate = DictSearch(
            data=self.raw_data,
            target={"TOCHeading": iden_name},
            return_func=DictSearch.return_parent_object
        ).result

        if not _intermediate:  # no result
            return None

        result = self.get_object(_intermediate[0][1])

        if isinstance(result, list):
            result = self.reduce_duplicates(result)

        return result

    @staticmethod
    def reduce_duplicates(result: list) -> Any:
        """Find most repeated value."""
        result_set = list(set(result))
        counts = [result.count(value) for value in result_set]
        return result_set[counts.index(max(counts))]

    # Property stuff
    ##################################################################################################################
    def get_prop(self):
        """ Main function to get all properties. """
        for p in self.config_prop:
            self.prop.add(p[1], self._get_prop_general(p[0], p[2]))

        if hasattr(self.iden, "molecular_formula"):
            self.prop.add("molar_mass", calc_molar_mass(self.iden.molecular_formula))

    def _get_prop_general(self, prop_name: str, quantity_check: bool = True):
        """Given a property name; try to find it and clean it up."""
        # Try to get prop dictionary
        _intermediate = DictSearch(
            data=self.raw_data,
            target={"TOCHeading": prop_name},
            return_func=DictSearch.return_parent_object
        ).result
        if not _intermediate:  # no data
            return None

        # get values out of prop dictionary
        result = self.get_object(_intermediate[0][1])
        result2 = self.get_value(_intermediate[0][1])

        if result is None and result2 is None:
            return None
        elif result is None and result2 is not None:
            result = result2
        elif result is not None and result2 is not None:
            if isinstance(result, str):
                result = result + result2
            else:  # list
                result.append(result2)

        # do quality control
        if quantity_check and self._contains_number(result):
            # Clean up property data
            result = self._clean_property_data(result)
        else:
            if isinstance(result, list) and len(result) > 1:
                result = result[0]

        return result

    @staticmethod
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

    @staticmethod
    def get_prop_keys(dict_) -> list[str]:
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

    @staticmethod
    def _contains_number(obj_in: Union[str, list]) -> bool:
        """ Checks list to see if it has a number in it anywhere."""
        _pattern = r'\d'
        if isinstance(obj_in, list):
            return any([bool(re.search(_pattern, value)) for value in obj_in])
        elif isinstance(obj_in, str):
            return bool(re.search(_pattern, obj_in))
        else:
            raise TypeError

    @staticmethod
    def _clean_property_data(prop_list: list[str]) -> Quantity:
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

        return quantity_list

    # Post processing
    ##################################################################################################################
    def post_processing(self):
        """An assortment of random methods to further clean the data."""
        if self.iden.inchi:
            self.iden.inchi = self.iden.inchi.strip("InChI=")

        if self.iden.names:
            self._post_processing_names()

        if self.iden.molecular_formula:
            self.iden.molecular_formula = MolecularFormula(self.iden.molecular_formula)

        if hasattr(self.prop, "density"):
            if isinstance(self.prop.density, (float, int)):
                self.prop.density = Quantity(f"{self.prop.density} g/mol")
            elif isinstance(self.prop.density, Quantity) and self.prop.density.dimensionless:
                self.prop.density = self.prop.density * Quantity(f"1 g/mol")

    def _post_processing_names(self):
        """ Everything to clean up names. """
        pattern = r"([0-9]+[-]{1}[0-9]+[-]{1}[0-9]+)|([0-9]{3})"  # looking for cas number
        self.iden.names = [name for name in self.iden.names if not re.search(pattern, name)]
        self.iden.names = [name for name in self.iden.names if not name.isupper()]  # remove all capitalized words
        self.iden.names = [name.strip().strip(",") for name in self.iden.names]
        self.iden.names = self._names_fix_segmented(self.iden.names)

        if self.iden.name not in self.iden.names:
            self.iden.names.insert(0, self.iden.name)

        self.iden.names = self._names_fix_duplicates(self.iden.names)
        self.iden.names = self.iden.names[:min([len(self.iden.names), 5])]

    @staticmethod
    def _names_fix_segmented(list_text: list[str]) -> list[str]:
        """ Takes test that is '####, ####-' --> '####-####' """
        out = []
        for text in list_text:
            split = re.split(r"(?<=[a-zA-Z]), (?=[1-9a-zA-Z])", text, maxsplit=1)
            if len(split) == 2 and split[1][-1] == "-":
                out.append(split[1] + split[0])
                continue

            out.append(text)

        return out

    @staticmethod
    def _names_fix_duplicates(list_text: list[str]) -> list[str]:
        """ Removes duplicate names """
        lower = [text.lower() for text in list_text]
        seen_index = set()
        seen = set()
        for i, text in enumerate(lower):
            if text in seen:
                continue

            seen.add(text)
            seen_index.add(i)

        return [list_text[index] for index in seen_index]


def get_files(path, pattern: str = "cid_*.json") -> list[str]:
    import glob
    import os

    # Find all json files
    file_list = []
    os.chdir(path)
    for files in glob.glob(pattern):
        file_list.append(files)  # filename with extension

    return file_list


def get_data(file_path) -> dict:
    encodings = ['utf-8', 'windows-1252', 'windows-1250', "latin-1"]
    for e in encodings:
        try:
            with open(file_path, "r", encoding=e) as f:
                text = f.read()
                json_data = json.loads(text)
                break
        except UnicodeDecodeError:
            pass
    else:
        raise RuntimeError(f"No valid encoding found for '{file_path}'.")

    return json_data


def local_run_multi():
    import time
    from pathlib import Path
    path = (Path(__file__).parent / Path("data"))
    # path = Path(r"C:\Users\nicep\Desktop\pubchem\json_files")
    file_list = get_files(path)

    for file in file_list:
        json_data = get_data(file)
        material = PubChemChemical(raw_data=json_data)
        print(material)
        material.pprint()
        time.sleep(0.1)

    print("done")


def get_prop_keys():
    from pathlib import Path
    path = (Path(__file__).parent / Path("data"))
    # path = Path(r"C:\Users\nicep\Desktop\pubchem\json_files")

    file_list = get_files(path)

    props = {}
    for file in file_list:
        print(f"{file}")
        json_data = get_data(file)
        keys = PubChemChemical.get_prop_keys(json_data)
        for prop in keys:
            if prop not in props:
                props[prop] = 1
            else:
                props[prop] += 1

    pprint.pprint(props)
    print("done")


def local_run_file():
    """ Get material from website. """
    from pathlib import Path
    #path = (Path(__file__).parent / Path("data/cid_7501.json"))
    path = Path(r"C:\Users\nicep\Desktop\pubchem\json_files\cid_120.json")

    json_data = get_data(path)
    material = PubChemChemical(raw_data=json_data)
    material.pprint()


def local_run():
    """ Get material from website. """
    material = PubChemChemical(cid=1111)
    material.pprint()


if __name__ == "__main__":
    local_run_multi()
    # local_run_file()
