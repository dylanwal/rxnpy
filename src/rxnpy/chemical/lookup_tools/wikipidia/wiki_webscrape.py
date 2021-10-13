"""
This code will extract data from chemical Wikipedia pages
"""


import requests
import re

from bs4 import BeautifulSoup
from bs4.element import NavigableString
# from Elements_Periodic import collapse_chemical_formula


def web_scrap_wiki(url_: str, data_want: list = None) -> dict:
    """
    This function takes in a URL from wikipedia and returns a dictionary of the chemistry information
    :param url_: wikipedia URL
    :param data_want: list of specific data you want returned
    :return: dictionary of data or False if no CAS # in table
    """
    # get website details
    response = requests.get(url=url_)
    soup = BeautifulSoup(response.content, 'html.parser')

    # determine if CAS # is present
    check_for_CAS = soup.body.findAll(text=re.compile('CAS'))
    if not check_for_CAS:
        return None

    # Dictionary that will contain the data
    data = dict()

    # get page title
    title = soup.find(id="firstHeading")
    data["Name"] = title.string

    # get all tables
    tables = soup.find_all('table')
    # select first table (which is the chemical data)
    rows = tables[0].find_all('tr')

    # Check table for CAS Number, to ensure right table was selected
    check = [row.text.find("CAS Number") for row in rows]
    if not any(check):
        print('No CAS Number found in table extracted from URL.')
        return None

    # Extract data
    IUPAC_count  = 0
    for row in rows:
        cells = row.find_all('td')

        # get two column data
        if len(cells) > 1:
            key_ = cells[0].text.strip()
            value_ = cells[1].text.strip()

            # cleaning data
            try:
                value_ = value_.replace(u'\xa0', ' ')
                value_ = value_.replace(u' Y', '')
            except:
                pass

            data[key_] = value_

        # get one column data
        elif len(cells) == 1:
            try:
                if 'IUPAC' in cells[0].text.split() and IUPAC_count == 0:
                    key_ = 'Preferred IUPAC name'
                    value_ = cells[0].text.split()[-1]
                    data[key_] = value_
                    IUPAC_count += 1
                    continue
            except:
                pass

            try:
                if cells[0].contents[0] == "Other names\n":
                    key_ = "Other names"
                    value_ = cells[0].contents[1].contents[:]
                    value_ = [elm for elm in value_ if isinstance(elm, NavigableString)]
                    data[key_] = value_
                    continue
            except:
                pass

            try:
                if cells[0].contents[0].contents[1].text == "SMILES":
                    key_ = "SMILES"
                    value_ = cells[0].contents[0].contents[3].contents[0].text
                    data[key_] = value_
                    continue
            except:
                pass

    # Reduce output
    if data_want:
        data = {k: v for k, v in data.items() if k in data_want}

    # make all keys lower case
    data = dict((key.lower(), value) for key, value in data.items())

    # check data, and modify if necessary
    data = cleaning_web_scrapped_data(data)

    return data


def cleaning_web_scrapped_data(data: dict) -> dict:
    """
    This function cleans some of the data extracted from Wikipidia
    Cleaning data from Wikipedia
    :param data: Dictionary of data collect from Wikipedia
    :return: Dictionary of cleaned data
    """

    # Remove any references on data
    for key, value in data.items():
        if value is None:
            continue
        elif type(value) is list:
            item_list = []
            for item_ in value:
                if bool(re.match(r".+\[+[0-9]+\]", item_)):
                    item_list.append(re.split(r"\[+[0-9]+\]", item_)[0])
                else:
                    item_list.append(item_)
            data[key] = item_list
        else:
            if bool(re.match(r".+\[+[0-9]+\]", value)):
                data[key] = re.split(r"\[+[0-9]+\]", value)[0]

    # Double check that CAS number is in correct format
    if "cas number" in data:
        if not re.match(r"[0-9]+[-]+[0-9]+[-]+[0-9]$", data["cas number"]):
            del data["cas number"]

    # for numerical properties split number and units
    if "molar mass" in data:
        if not type(data["molar mass"]) in {float, int}:
            value = data["molar mass"].split(' ')
            value = re.sub(r"[^0-9|.]", "", value[0])
            data["molar mass"] = {"value": float(value), "units": "g/mol"}

    if "density" in data:
        if not type(data["density"]) in {float, int}:
                value = data["density"].split(' ')[0].split("-")
                value = re.sub(r"[^0-9|.]", "", value[0])
                data["density"] = {"value": float(value), "units": "g/mL"}

    # Chemical formula
    if "chemical formula" in data:  # delete extra if more than one provided
        if len(data["chemical formula"].split(' ')) > 1:
            data["chemical formula"] = data["chemical formula"].split(' ')[0]

        # reduce chemical formulas
        data["chemical formula"] = collapse_chemical_formula(data["chemical formula"])

    # names
    name_list = ["name", "preferred iupac name", "other names"]
    add_names = []
    for name_ in name_list:
        if name_ in data and data[name_] is not None:
            if type(data[name_]) is list:
                add_names = add_names + data[name_]
            else:
                add_names.append(data[name_])

    if add_names:
        data["additional names"] = add_names

    return data


def main():
    import pprint
    web_page = "https://en.wikipedia.org/wiki/Styrene"
    # "https://en.wikipedia.org/wiki/1,4-Butanediol"
    # "https://en.wikipedia.org/wiki/Sec-Butyllithium"
    # "https://en.wikipedia.org/wiki/1,5-Pentanediol"

    data = web_scrap_wiki(web_page)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)


if __name__ == '__main__':
    main()