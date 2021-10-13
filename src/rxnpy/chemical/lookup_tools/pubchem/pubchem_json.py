from pathlib import Path
from urllib.request import urlretrieve
from time import sleep
from random import randint

folder = Path(r"C:\Users\nicep\Desktop\pubchem\json_files")
stop = 3

for i in range(1, 10_000):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{i}/JSON/"
    flag = True
    ii = 0
    while flag:
        try:
            urlretrieve(url, (folder / f"cid_{i}.json").resolve())
            flag = False

        except Exception as e:
            print(e)
            sleep(60)
            ii += 1
            if ii == 5:
                exit()

    sleep(0.1)
    if i % stop == 0:
        stop = randint(5, 8)
        sleep(randint(3, 15))

    print(i)

