"""

This is to collect data to JSON.

"""

from typing import Union
import os
from pathlib import Path
from urllib.request import urlretrieve
from time import sleep
from random import randint

from rxnpy.chemical.lookup_tools.logger_lookup import look_up_logger


def download_from_pubchem(cid: int, path_save: Union[Path, str] = os.getcwd()):
    """ download_from_pubchem

    Downloads a single pubchem JSON.

    Parameters
    ----------
    cid: int
        cid
    path_save: Path, str
        location where json will be saved

    Returns
    -------
    None

    Notes
    -----
    * pauses add to avoid 'denial-of-service' error

    """
    if isinstance(path_save, str):
        path_save = Path(path_save)

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
    flag = True
    ii = 0
    while flag:
        try:
            urlretrieve(url, (path_save / f"cid_{cid}.json").resolve())
            flag = False

        except Exception as e:
            # pause to avoid triggering 'denial-of-service' error
            sleep(60)
            ii += 1
            if ii == 5:  # stop completely if it can't get the JSON
                look_up_logger.error(f"PubChem: download of cid_{cid} failed due to too many failed tries.")
                raise RuntimeError(e)

    look_up_logger.debug(f"PubChem: cid_{cid} downloaded.")


def batch_download_from_pubchem(cid_start: int, cid_end: int,
                                path_save: Union[Path, str] = os.getcwd(), pause: float = 3):
    """ batch_download_from_pubchem

    Downloads a batch (multiple pubchem files) JSON.

    Parameters
    ----------
    cid_start: int
        start cid
    cid_end: int
        end cid
    path_save: Path, str
        location where json will be saved
    pause: float
        pause interval, how often a pause should occur

    Returns
    -------
    None

    Notes
    -----
    * pauses add to avoid 'denial-of-service' error

    """
    look_up_logger.info(f"PubChem: batch download beginning: cid_{cid_start} - cid_{cid_end}\n\t\tSaving to: "
                        f"{path_save}")
    if isinstance(path_save, str):
        path_save = Path(path_save)

    for i in range(cid_start, cid_end + 1):
        download_from_pubchem(cid=i, path_save=path_save)

        # pauses add to avoid 'denial-of-service' error
        sleep(0.1)
        if i % pause == 0:
            pause = randint(5, 8)
            sleep(randint(3, 15))

    look_up_logger.info(f"PubChem: batch download done: cid_{cid_start} - cid_{cid_end}")


def test():
    import logging

    look_up_logger.setLevel(logging.DEBUG)

    cwd = os.getcwd()
    folder = Path(cwd + r"\data")
    batch_download_from_pubchem(1, 5, path_save=folder)


if __name__ == "__main__":
    test()
