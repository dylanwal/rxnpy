"""
This code will extract data from chemical Sigma Aldrich pages
"""

import requests
from bs4 import BeautifulSoup
import re


def web_scrap_sigma(url_: str, data_want: list = None) -> dict:
    """
    This function takes in a URL from wikipedia and returns a dictionary of the chemistry information
    :param url_: wikipedia URL
    :param data_want: list of specific data you want returned
    :return: dictionary of data or False if no CAS # in table
    """
    # Dictionary that will contain the data
    data = dict()

    # get website details
    response = requests.get(url=url_)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Narrow into top data
    product_info = soup.find(class_="productInfo")

    # Data from gray box name data
    name = product_info.find(itemprop="name").text.strip()
    try:
        other_names = product_info.find(class_="synonym").text.split()
        other_names = other_names[1:]
        other_names.insert(0, name)
        other_names2 = []
        for item in other_names:
            if item[-1] == ",":
                other_names2 = item[:-1]
            else:
                other_names2 = item
        data["additional names"] = other_names
    except AttributeError:
        data["additional names"] = [name]

    # Data from gray box
    raw_data = product_info.find(class_="clearfix")
    raw_data = raw_data.select("div p")
    raw_data = [x.text.split() for x in raw_data]
    for line in raw_data:
        if line[0] == "CAS":
            if re.match(r"[0-9]+[-]+[0-9]+[-]+[0-9]$", line[2]):  # Check format
                data["cas number"] = line[2]
        if line[0] == "Molecular":
            data["molecular weight"] = {"value": float(line[2]), "units": "g/mol"}

    # Narrow into bottom data
    property_info = soup.find(id="productPurchaseContainer")
    left = property_info.find_all(class_="lft")
    left = [value.text.replace('\n', '').replace('\t', '').strip() for value in left if value.text is not None]
    right = property_info.find_all(class_="rgt")
    right = [value.text.replace('\n', '').replace('\t', '').replace("\xa0", ' ').strip() for value in right if value.text is not None]
    table = list(zip(left, right))
    for item in table:
        if item[0] == "":
            continue
        else:
            if item[0].lower() == "density":
                try:
                    data[item[0]] = {"value": float(item[1].split(" ")[0]), "units": "g/ml"}
                except:
                    continue
            elif item[0].lower() == "form":
                data["phase"] = item[1]
            elif item[0].lower() == "bp":
                data["boiling point"] = item[1]
            elif item[0].lower() == "mp":
                data["melting point"] = item[1]
            elif item[0].lower() == "smiles string":
                data["smiles"] = item[1]
            elif item[0] != '':
                data[item[0]] = item[1]

    # Reduce output
    if data_want:
        data = {k: v for k, v in data.items() if k in data_want}

    # make all keys lower case
    data = dict((key.lower(), value) for key, value in data.items())

    return data


def main():
    import pprint
    web_page = "https://www.sigmaaldrich.com/catalog/product/sial/s4972?lang=en&region=US"\
    #  "https://www.sigmaaldrich.com/catalog/product/aldrich/g3407?lang=en&region=US"
    #  "https://www.sigmaaldrich.com/catalog/product/sial/s4972?lang=en&region=US"    styrene

    data = web_scrap_sigma(web_page)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)


if __name__ == '__main__':
    main()