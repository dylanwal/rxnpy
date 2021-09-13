from string import ascii_uppercase
import re
import pandas as pd
import pint

# from Wiki_web_page import web_scrap_wiki
# from Sigma_web_page import web_scrap_sigma


u = pint.UnitRegistry()

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 20)

data_search_keys = ['Name', 'Preferred IUPAC name', "SMILES", "Other names", 'Melting point', 'Molar mass', 'Density',
                    'Chemical formula', 'CAS Number', 'Boiling point', 'Appearance', 'Main hazards',
                    'Refractive index (nD)']


def open_excel(file_name, sheet_name):
    # connect with Open Excel Application
    try:
        ExcelApp = win32com.client.GetActiveObject("Excel.Application")
    except AttributeError:
        # Corner case dependencies.
        import os
        import sys
        import shutil
        # Remove cache and try again.
        MODULE_LIST = [m.__name__ for m in sys.modules.values()]
        for module in MODULE_LIST:
            if re.match(r'win32com\.gen_py\..+', module):
                del sys.modules[module]
        shutil.rmtree(os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp', 'gen_py'))
        from win32com import client
        ExcelApp = client.gencache.EnsureDispatch('Excel.Application')
        print("Open_Excel_exception.")

    # select workbook
    try:
        Excel_workbook = ExcelApp.Workbooks(file_name)
        worksheet = Excel_workbook.Worksheets(sheet_name)
    except pywintypes.com_error:
        for i in range(15):
            try:
                Excel_workbook = ExcelApp.Workbooks(i)
                worksheet = Excel_workbook.Worksheets(sheet_name)
                break
            except pywintypes.com_error:
                pass

    # select worksheet
    return worksheet


def get_excel_data(ws):
    """
    Parses Ingredients table
    :param ws: Excel worksheet
    :return: pandas DataFrame
    """
    raw_data = ws.Range("A1:Z50").Value

    # get "Ingredients" location
    for row_index in range(len(raw_data)):
        for col_index in range(len(raw_data[0])):
            cell = raw_data[row_index][col_index]
            if cell is None:
                continue
            elif cell.lower() == 'Ingredients'.lower():
                offset = [row_index, col_index]
                break
        else:
            continue
        break

    start_coord = [offset[0] + 2, offset[1]]  # the 2 is to skip a row below the header for a second header

    # Grab row index (chemical names)
    chemicals = []
    dict_for_pd = {}
    for col_index in range(start_coord[1], start_coord[1]+50):
        header = raw_data[start_coord[0]][col_index]
        if header is None:
            break
        elif header.lower() == "Name".lower():
            for row_index in range(start_coord[0]+2, start_coord[0]+25):
                chemical = raw_data[row_index][col_index]
                if chemical is None:
                    break
                else:
                    chemicals.append(chemical)
        else:
            data = []
            counter = 0
            for row_index in range(start_coord[0]+1, start_coord[0]+2+len(chemicals)):
                data_ = raw_data[row_index][col_index]
                if counter != 0:  # This is to prevent a NaN error when dict is converted into dataframe
                    data.append(data_)
                elif counter == 0 and data_ is None:
                    data.append("None")
                    counter += 1
                else:
                    counter += 1
                    data.append(data_)
            dict_for_pd[header.lower()] = data

    return pd.DataFrame(dict_for_pd, index=["units"] + chemicals)


def put_data_back_Excel(ws, df_new):
    # find first header
    for i in excel_coord():
        value = ws.Range(i).Value
        if value is None:
            continue
        elif value.lower() == df_new.columns[0]:
            coord_start = list(i)
            coord_start = coord_start[0] + str(int(coord_start[1])+1)
            break

    coord_end = list(ascii_uppercase)[len(df_new.columns)] + str(int(list(coord_start)[1])+len(df_new.index)-1)
    data_range = coord_start + ":" + coord_end

    data_out = df_new.values.tolist()

    # put data back into Excel
    ws.Range(data_range).Value = data_out


def excel_coord(start=1, end=27):
    """ Generates outputs from  A1 to Z26 (No double letters)"""
    uppercase_letters = list(ascii_uppercase)
    for i in range(start, end):
        # Vertical line (complete)
        for ii in range(start, i+1):
            yield uppercase_letters[(i % 26)-1] + str(ii)
        # horizontal bottom line (fill)
        for iii in range(start, i):
            yield uppercase_letters[(iii % 26)-1] + str(i)

    exit("Excel generator reached its end point.")


def do_lookup(df):
    """
    :param df:
    :return:
    """
    cal_errors = []
    for chemical in df.index:
        if chemical != "units":
            # find do look up:
            data = google_search(chemical)

            # put data into df
            for key, value in data.items():
                if key in df.columns:
                    if key == "density":
                        if "phase" in df.columns and type(df["phase"][chemical]) == str and \
                                df["phase"][chemical].lower() not in {"solution", "solid", "gas"}:
                            value_and_units = float(value["value"]) * u[value["units"]]
                            df.at[chemical, key] = value_and_units.to(u[df[key]["units"]]).magnitude
                        elif "phase" not in df.columns or df["phase"][chemical] is None:
                            value_and_units = float(value["value"]) * u[value["units"]]
                            df.at[chemical, key] = value_and_units.to(u[df[key]["units"]]).magnitude
                    elif key == "molar mass":
                        value_and_units = float(value["value"]) * u[value["units"]]
                        df.at[chemical, key] = value_and_units.to(u[df[key]["units"]]).magnitude
                    elif key == "concentration":
                        continue
                    elif key == "additional names":
                        add_names = ""
                        for name_ in value:
                            add_names = add_names + name_ + ', '
                        df.at[chemical, key] = add_names[:-2]
                    else:
                        df.at[chemical, key] = value
                elif key in "smiles":
                    df.at[chemical, "(big)smiles"] = value

    return df, cal_errors


def google_search(chemical_name: str) -> dict:
    """
    Given a chemical name, it will google search and if a Wikipedia or Sigma Aldrich page pops up than
    it will extract any available data
    :param chemical_name: chemical name
    :return: dictionary of all data collected
    """
    # does google search
    web_pages = [url_ for url_ in search(chemical_name, tld="co.in", num=20, stop=20, pause=.1)]

    # check for Wikipedia or Sigma page and grab data
    wiki_count = 0
    sigma_count = 0
    wiki_data = {}
    sigma_data = {}
    for web_page in web_pages:
        if web_page.find("https://en.wikipedia.org/wiki/") != -1 and wiki_count == 0:
            wiki_count += 1  # We only want to look through first Wikipedia page
            wiki_data = web_scrap_wiki(web_page, data_search_keys)  # Web scrap Wikipedia page

        elif web_page.find("https://www.sigmaaldrich.com/catalog/product/") != -1 and sigma_count == 0:
            sigma_count += 1  # We only want to look through first Wikipedia page
            sigma_data = web_scrap_sigma(web_page)  # Web scrap Sigma page

    # combine the data collected
    data = {}
    if wiki_data and sigma_data:
        all_keys = set(list(wiki_data.keys()) + list(sigma_data.keys()))
        for key_ in all_keys:
            if key_ == 'additional names':
                if key_ in sigma_data and key_ in wiki_data:
                    values = set([x.lower() for x in sigma_data[key_]] +
                                 [x.lower() for x in wiki_data[key_]])
                    data[key_] = values
                elif key_ in sigma_data:
                    values = set([x.lower() for x in sigma_data[key_]])
                    data[key_] = values
                elif key_ in wiki_data:
                    values = set([x.lower() for x in wiki_data[key_]])
                    data[key_] = values
            else:
                try:
                    data[key_] = sigma_data[key_]
                except KeyError:
                    data[key_] = wiki_data[key_]
    elif wiki_data:
        data = wiki_data
        data['additional names'] = set([x.lower() for x in data['additional names']])
    elif sigma_data:
        data = sigma_data
        data['additional names'] = set([x.lower() for x in data['additional names']])

    return data


def main(file_=1, sheet_='CRIPT'):
    try:
        # Connect to Excel File
        excel_worksheet = open_excel(file_, sheet_)

        # Extract data
        df = get_excel_data(excel_worksheet)

        # Do lookup
        df_new, cal_errors = do_lookup(df)

        # Place data back
        if df_new is not None:
            put_data_back_Excel(excel_worksheet, df_new)

        # Status Output
        if not cal_errors:
            excel_worksheet.Range("F1").Value = "Lookup Complete!" + f"  {datetime.now()}"
            excel_worksheet.Range("I1").Value = ""
        else:
            excel_worksheet.Range("F1").Value = f"{len(cal_errors)} concerns.." + f"  {datetime.now()}"
            excel_worksheet.Range("I1").Value = "Check the following errors:   " + '\n'.join(cal_errors)

    except Exception:
        # Status Output
        excel_worksheet.Range("F1").Value = "Lookup Error!!!" + f"  {datetime.now()}"
        excel_worksheet.Range("I1").Value = "Error:" + format_exc()


if __name__ == '__main__':
    main()