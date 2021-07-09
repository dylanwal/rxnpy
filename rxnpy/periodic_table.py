"""
This file contains a list of elements and a function to check chemical formulas to ensure they are reduced completely.
"""

import re

elements = {
 'Ac': 'Actinium',
 'Ag': 'Silver',
 'Al': 'Aluminum',
 'Am': 'Americium',
 'Ar': 'Argon',
 'As': 'Arsenic',
 'At': 'Astatine',
 'Au': 'Gold',
 'B': 'Boron',
 'Ba': 'Barium',
 'Be': 'Beryllium',
 'Bh': 'Bohrium',
 'Bi': 'Bismuth',
 'Bk': 'Berkelium',
 'Br': 'Bromine',
 'C': 'Carbon',
 'Ca': 'Calcium',
 'Cd': 'Cadmium',
 'Ce': 'Cerium',
 'Cf': 'Californium',
 'Cl': 'Chlorine',
 'Cm': 'Curium',
 'Cn': 'Copernicium',
 'Co': 'Cobalt',
 'Cr': 'Chromium',
 'Cs': 'Cesium',
 'Cu': 'Copper',
 'Db': 'Dubnium',
 'Ds': 'Darmstadtium',
 'Dy': 'Dysprosium',
 'Er': 'Erbium',
 'Es': 'Einsteinium',
 'Eu': 'Europium',
 'F': 'Fluorine',
 'Fe': 'Iron',
 'Fl': 'Flerovium',
 'Fm': 'Fermium',
 'Fr': 'Francium',
 'Ga': 'Gallium',
 'Gd': 'Gadolinium',
 'Ge': 'Germanium',
 'H': 'Hydrogen',
 'He': 'Helium',
 'Hf': 'Hafnium',
 'Hg': 'Mercury',
 'Ho': 'Holmium',
 'Hs': 'Hassium',
 'I': 'Iodine',
 'In': 'Indium',
 'Ir': 'Iridium',
 'K': 'Potassium',
 'Kr': 'Krypton',
 'La': 'Lanthanum',
 'Li': 'Lithium',
 'Lr': 'Lawrencium',
 'Lu': 'Lutetium',
 'Lv': 'Livermorium',
 'Mc': 'Moscovium',
 'Md': 'Mendelevium',
 'Mg': 'Magnesium',
 'Mn': 'Manganese',
 'Mo': 'Molybdenum',
 'Mt': 'Meitnerium',
 'N': 'Nitrogen',
 'Na': 'Sodium',
 'Nb': 'Niobium',
 'Nd': 'Neodymium',
 'Ne': 'Neon',
 'Nh': 'Nihonium',
 'Ni': 'Nickel',
 'No': 'Nobelium',
 'Np': 'Neptunium',
 'O': 'Oxygen',
 'Og': 'Oganesson',
 'Os': 'Osmium',
 'P': 'Phosphorus',
 'Pa': 'Protactinium',
 'Pb': 'Lead',
 'Pd': 'Palladium',
 'Pm': 'Promethium',
 'Po': 'Polonium',
 'Pr': 'Praseodymium',
 'Pt': 'Platinum',
 'Pu': 'Plutonium',
 'Ra': 'Radium',
 'Rb': 'Rubidium',
 'Re': 'Rhenium',
 'Rf': 'Rutherfordium',
 'Rg': 'Roentgenium',
 'Rh': 'Rhodium',
 'Rn': 'Radon',
 'Ru': 'Ruthenium',
 'S': 'Sulfur',
 'Sb': 'Antimony',
 'Sc': 'Scandium',
 'Se': 'Selenium',
 'Sg': 'Seaborgium',
 'Si': 'Silicon',
 'Sm': 'Samarium',
 'Sn': 'Tin',
 'Sr': 'Strontium',
 'Ta': 'Tantalum',
 'Tb': 'Terbium',
 'Tc': 'Technetium',
 'Te': 'Tellurium',
 'Th': 'Thorium',
 'Ti': 'Titanium',
 'Tl': 'Thallium',
 'Tm': 'Thulium',
 'Ts': 'Tennessine',
 'U': 'Uranium',
 'V': 'Vanadium',
 'W': 'Tungsten',
 'Xe': 'Xenon',
 'Y': 'Yttrium',
 'Yb': 'Ytterbium',
 'Zn': 'Zinc',
 'Zr': 'Zirconium'}



def collapse_chemical_formula(chemical_formula):
    """
    Given a chemical formula return a collapsed version.
    :param chemical_formula:
    :return:
    """
    # split formula up
    split_formula = re.findall(r'[A-Z]{1}[a-z]*|\d+', chemical_formula)

    # put data into dictionary
    chemical_list = {}
    for index, entry in enumerate(split_formula):
        if not entry.isnumeric():
            if entry not in elements:  # ensure all letter groups are element abbreviations
                return ""
            if entry in chemical_list:
                try:
                    num_ = split_formula[index+1]
                except IndexError:
                    num_ = "1"
                if num_.isnumeric():
                    chemical_list[entry] = int(num_) + chemical_list[entry]
                else:
                    chemical_list[entry] = 1 + chemical_list[entry]
            else:
                try:
                    num_ = split_formula[index + 1]
                except IndexError:
                    num_ = "1"
                if num_.isnumeric():
                    chemical_list[entry] = int(num_)
                else:
                    chemical_list[entry] = 1

    # convert dictionary back to formula
    chemical_formula = ""
    for key, value in chemical_list.items():
        chemical_formula = chemical_formula + key + str(value)

    return chemical_formula


if __name__ == '__main__':
    chemical_formula_in = "C1H3OH63Cr2CCCOOO"
    chemical_formula_out = collapse_chemical_formula(chemical_formula_in)
    print(f"{chemical_formula_in}  --> {chemical_formula_out}")