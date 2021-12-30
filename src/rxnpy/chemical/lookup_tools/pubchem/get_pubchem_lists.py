from typing import Dict, List
import json

from dictpy import DictSearch


def get_prop_list(_dict: Dict) -> List[str]:
    """From Pubchem dict, return list of properties"""
    _expt_section = DictSearch(
        data=_dict,
        target={"TOCHeading": "Experimental Properties"},
        return_func=DictSearch.return_parent_object)
    if not _expt_section.result:
        return []
    else:
        _expt_section = _expt_section.result[0][1]

    _props_list = DictSearch(
        data=_expt_section,
        target={"TOCHeading": "*"})
    return [_prop[1]["TOCHeading"] for _prop in _props_list.result]


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
        if k == 500:
            break

    def get_data(file_path: Path) -> dict:
        with open(file_path, "r", encoding="latin-1") as f:
            _text = f.read()
            _json_data = json.loads(_text)

        return _json_data


    # load in json files
    json_data = []
    for file in files_list:
        json_data.append(get_data(file))

    # run extraction on json files
    props = {}
    for _data in json_data:
        props_list = get_prop_list(_data)
        for prop in props_list:
            if prop not in props:
                props[prop] = 1
            else:
                props[prop] += 1

    print(json.dumps(props, indent=4))
    print("done")
