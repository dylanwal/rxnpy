import pubchempy as pcp
import csv
from time import sleep
from random import randint

data_labels = ["cid", "canonical_smiles", "molecular_formula", "iupac_name", "inchi", "inchikey", "synonyms"]
stop = 6

with open("chempub_list5.csv", "w") as f:
    wr = csv.writer(f, quoting=csv.QUOTE_ALL)
    for i in range(26_639, 50_000, 1):
        c = pcp.Compound.from_cid(i)
        data = [getattr(c, label) if hasattr(c, label) else None for label in data_labels]
        if data[4] is not None:
            data[4] = data[4].strip("InChI=")
        if data[6] is not None:
            data[6] = "||".join(data[6][0:min(5, len(c.synonyms))])
        wr.writerow(data)

        if i % stop == 0:
            stop = randint(5, 10)
            sleep(randint(5, 15))

        print(i)

