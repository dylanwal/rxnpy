import json
import os

from rxnpy.chemical import PubChemChemical
from rxnpy.utilities.working_with_files import get_files, get_json


def single_process(file):
    json_data = get_json(file)
    material = PubChemChemical(raw_data=json_data)
    json_ = material.to_JSON()
    with open(f"C://Users//nicep//Desktop//pubchem//clean//cid_{material.iden.pubchem_cid}.json",
              "w", encoding='utf-8') as f:
        json.dump(json_, f, ensure_ascii=False, indent=4)


def local_run():
    import time
    from pathlib import Path

    path = Path(r"C:\Users\nicep\Desktop\pubchem\json_files")
    file_list = get_files(path)

    start = time.time()

    for file in file_list:
        single_process(file)

    print((time.time()-start))

    print("done")


def local_run_multi():
    import time
    from pathlib import Path
    import multiprocessing

    path = Path(r"C:\Users\nicep\Desktop\pubchem\json_files")
    file_list = get_files(path)

    start = time.time()

    pool = multiprocessing.Pool(os.cpu_count() - 1)
    pool.map(single_process, file_list)

    print(time.time() - start)

    print("done")


if __name__ == '__main__':
    local_run()
    # local_run_multi()
