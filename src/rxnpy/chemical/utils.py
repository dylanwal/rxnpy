
from typing import Union

from rxnpy import Quantity
from rxnpy.chemical.sub_objects.molecular_formula import MolecularFormula
from rxnpy.chemical.periodic_table import periodic_table


def calc_molar_mass(mol_form: Union[str, MolecularFormula]) -> Quantity:
    if isinstance(mol_form, str):
        mol_form = MolecularFormula(mol_form)

    molar_mass = 0
    for element, num in mol_form:
        molar_mass += num * periodic_table[element].atomic_mass

    return molar_mass


def local_run():
    mol_form = "C9H17NO4"
    print(calc_molar_mass(mol_form))


if __name__ == '__main__':
    local_run()
