import json
import time
import urllib.request
import pprint


from rxnpy.config.pubchem import config_PubChem
from rxnpy.chemical.chemical import Chemical
from rxnpy.chemical.sub_objects.property import Prop
from rxnpy.chemical.utils import calc_molar_mass
from rxnpy.chemical.lookup_tools.logger_lookup import logger_look_up
from rxnpy.chemical.lookup_tools.pubchem.iden_parse import get_iden
from rxnpy.chemical.lookup_tools.pubchem.prop_parse import get_prop


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
    logger_look_up.debug(f"PubChem: cid_{cid} attempting to download.")
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
    flag = True
    ii = 0
    while flag:
        try:
            # do web request
            with urllib.request.urlopen(url) as url_data:
                # load data into a dictionary
                json_data = json.loads(url_data.read().decode("UTF-8"))
            logger_look_up.debug(f"PubChem: cid_{cid} downloaded.")
            return json_data

        except Exception as e:  # if web request fails
            # pause to avoid triggering 'denial-of-service' error
            time.sleep(5)
            ii += 1
            if ii == 5:  # stop completely if it can't get the JSON
                logger_look_up.error(f"PubChem: download of cid_{cid} failed due to too many failed tries.")
                raise RuntimeError(e)


class PubChemChemical(Chemical):
    """ PubChemMaterial

    Gets data from PubChem and cleans it.

    Attributes
    ----------
    raw_data: dict
        dictionary of JSON from PubChem

    """
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
            raw_data = download_from_pubchem(cid)
        self.raw_data = raw_data

        super().__init__(iden=get_iden(raw_data), prop=get_prop(raw_data))
        self.post_init()

        logger_look_up.debug(f"PubChem: cid_{self.iden.pubchem_cid} finish obtaining identifiers and properties.")

    def post_init(self):
        if hasattr(self.iden, "mol_form"):
            self.prop.add(Prop("molar_mass", calc_molar_mass(self.iden.mol_form)))

    def to_JSON(self, remove_none: bool = True, skip: set[str] = None) -> dict:
        if skip is None:
            skip = {"raw_data"}
        return super().to_JSON(remove_none, skip=skip)


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
    encodings = ['utf-8', 'windows-1250', 'windows-1252', "latin-1"] #'utf-8'
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

    logger_look_up.info(f"decoding {file_path} with: {e}")
    return json_data


def local_run_multi():
    import time
    from pathlib import Path
    # path = (Path(__file__).parent / Path("data"))
    path = Path(r"C:\Users\nicep\Desktop\pubchem\json_files")
    file_list = get_files(path)

    for file in file_list[100:300]:
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
    # path = (Path(__file__).parent / Path("data/cid_7501.json"))
    path = Path(r"C:\Users\nicep\Desktop\pubchem\json_files\cid_2710.json")

    json_data = get_data(path)
    material = PubChemChemical(raw_data=json_data)
    material.pprint()
    json_ = material.to_JSON()
    print("done")


def local_run():
    """ Get material from website. """
    material = PubChemChemical(cid=1001)
    material.pprint()


if __name__ == "__main__":
    # local_run_multi()
    local_run_file()
    # local_run()
