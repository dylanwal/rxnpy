
from pathlib import Path
import pprint

from rxnpy.chemical import Chemical
from rxnpy.utilities.working_with_files import get_files, get_json


def single_process(file):
    json_data = get_json(file)
    return Chemical.load(json_data)


def load_multi():
    path = Path(r"C:\Users\nicep\Desktop\pubchem\clean")
    file_list = get_files(path)

    props = {}
    for file in file_list:
        chem = single_process(file)
        for prop in chem.prop:
            if prop.key not in props:
                props[prop.key] = 1
            else:
                props[prop.key] += 1

            if prop.key == "polymerization":
                print(f"{chem}: {prop}")

    pprint.pprint(props)


def load_single():
    path = Path(r"C:\Users\nicep\Desktop\pubchem\clean\cid_7294.json")
    chem = single_process(path)
    print(chem.pprint())


if __name__ == '__main__':
    # load_single()
    load_multi()
