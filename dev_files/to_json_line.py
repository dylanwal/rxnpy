""" Groups jsons into a large line json. """
from pathlib import Path

from rxnpy.utilities.working_with_files import save_to_jsonl, get_multi_json

path = Path(r"C:\Users\nicep\Desktop\pubchem\clean")
json_gen = get_multi_json(path, chunk=1000)
for j in json_gen:
    start = j[0]["iden"]["pubchem_cid"]
    end = j[-1]["iden"]["pubchem_cid"]
    save_to_jsonl(r"C:\Users\nicep\Desktop\pubchem\clean_lines", f"cid_{start}_to_{end}", j)
    print(f"finished: {start} - {end}")

print("done")
