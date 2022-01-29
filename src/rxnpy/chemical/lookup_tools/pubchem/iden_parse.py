from typing import Union, Any
import re

from dictpy import DictSearch

from rxnpy.config.pubchem import config_PubChem
from rxnpy.chemical.sub_objects.identifiers import Iden


def get_iden(data_dict: dict) -> Iden:
    iden_dict = {"name": get_name(data_dict), "names": get_names(data_dict), "pubchem_cid": get_cid(data_dict)}

    for i in config_PubChem.pubchem_identities:
        iden_dict[i[1]] = get_iden_general(data_dict, i[0])

    iden = Iden(**iden_dict)
    iden_clean_up(iden)
    return iden


def get_name(data_dict) -> str:
    """ Get chemical name. """
    return str(
        DictSearch(data=data_dict, target={"RecordTitle": "*"},
                   return_func=DictSearch.return_current_object).result[0][1]["RecordTitle"]
    )


def get_names(data_dict) -> Union[list[str], None]:
    """ Get chemical names. """
    _intermediate = DictSearch(data=data_dict, target={"TOCHeading": "Depositor-Supplied Synonyms"},
                               return_func=DictSearch.return_parent_object).result
    if not _intermediate:  # section not present
        return None

    result = get_object(_intermediate[0][1])
    if isinstance(result, str):
        return [result]

    return result[:8]


def get_cid(data_dict: dict) -> int:
    return int(DictSearch(
        data=data_dict,
        target={"RecordNumber": "*"},
        return_func=DictSearch.return_current_object
    ).result[0][1]["RecordNumber"])


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


def get_iden_general(data_dict, iden_name: str):
    _intermediate = DictSearch(
        data=data_dict,
        target={"TOCHeading": iden_name},
        return_func=DictSearch.return_parent_object
    ).result

    if not _intermediate:  # no result
        return None

    result = get_object(_intermediate[0][1])

    if isinstance(result, list):
        result = reduce_duplicates(result)

    return result


def reduce_duplicates(result: list) -> Any:
    """Find most repeated value."""
    result_set = list(set(result))
    counts = [result.count(value) for value in result_set]
    return result_set[counts.index(max(counts))]


def iden_clean_up(iden: Iden):
    if iden.inchi:
        iden.inchi = iden.inchi.strip("InChI=")

    if iden.names:
        names_cleanup(iden)


def names_cleanup(iden: Iden):
    """ Everything to clean up names. """
    pattern = r"([0-9]+[-]{1}[0-9]+[-]{1}[0-9]+)|([0-9]{3})"  # looking for cas number
    iden.names = [name for name in iden.names if not re.search(pattern, name)]
    iden.names = [name for name in iden.names if not name.isupper()]  # remove all capitalized words
    iden.names = [name.strip().strip(",") for name in iden.names]
    iden.names = names_fix_segmented(iden.names)

    if iden.name not in iden.names:
        iden.names.insert(0, iden.name)

    iden.names = names_fix_duplicates(iden.names)
    iden.names = iden.names[:min([len(iden.names), 5])]


def names_fix_segmented(list_text: list[str]) -> list[str]:
    """ Takes test that is '####, ####-' --> '####-####' """
    out = []
    for text in list_text:
        split = re.split(r"(?<=[a-zA-Z]), (?=[1-9a-zA-Z])", text, maxsplit=1)
        if len(split) == 2 and split[1][-1] == "-":
            out.append(split[1] + split[0])
            continue

        out.append(text)

    return out


def names_fix_duplicates(list_text: list[str]) -> list[str]:
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
