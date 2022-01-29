from typing import Union

from dictpy import Serializer

from rxnpy.chemical.sub_objects.molecular_formula import MolecularFormula
from rxnpy.utilities.decorators import freeze_class


@freeze_class
class Iden(Serializer):
    """

    Attributes
    ----------
    name: str
        preferred name
    names: list[str]
        additional names, abbreviations, short hands for the material
    cas: str
        CAS number
    smiles: str
        simplified molecular-input line-entry system
    mol_for: MolecularFormula

    pubchem_cid: int
            PubChem CID
    inchi: str
        IUPAC International Chemical Identifier
    inchi_key: str
        a hashed version of the full InChI
      """
    
    def __init__(
            self,
            name: str,
            names: Union[str, list[str]] = None,
            cas: str = None,
            bigsmiles: str = None,
            smiles: str = None,
            mol_for: Union[MolecularFormula, str] = None,
            pubchem_cid: int = None,
            inchi: str = None,
            inchi_key: str = None,
            **kwargs
    ):

        self._name = None
        self._names = None
        
        self.name = name

        # adding name to names
        if names is None:
            names = [name]
        elif isinstance(names, list):
            if name not in names:
                names.append(name)

        self.names = names

        self._cas = None
        self.cas = cas

        self._bigsmiles = None
        self.bigsmiles = bigsmiles

        self._smiles = None
        self.smiles = smiles

        self._mol_for = None
        self.mol_for = mol_for

        self._pubchem_cid = None
        self.pubchem_cid = pubchem_cid

        self._inchi = None
        self.inchi = inchi

        self._inchi_key = None
        self.inchi_key = inchi_key

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        text = f"{self.name}"
        if self.mol_for is not None:
            text += f" ({self.mol_for})"

        return text

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def names(self):
        return self._names

    @names.setter
    def names(self, names):
        self._names = names

    @property
    def cas(self):
        return self._cas

    @cas.setter
    def cas(self, cas):
        self._cas = cas

    @property
    def bigsmiles(self):
        return self._bigsmiles

    @bigsmiles.setter
    def bigsmiles(self, bigsmiles):
        self._bigsmiles = bigsmiles

    @property
    def smiles(self):
        return self._smiles

    @smiles.setter
    def smiles(self, smiles):
        self._smiles = smiles

    @property
    def mol_for(self):
        return self._mol_for

    @mol_for.setter
    def mol_for(self, mol_for):
        if not isinstance(mol_for, MolecularFormula) and mol_for is not None:
            mol_for = MolecularFormula(mol_for)
        self._mol_for = mol_for

    @property
    def pubchem_cid(self):
        return self._pubchem_cid

    @pubchem_cid.setter
    def pubchem_cid(self, pubchem_cid):
        self._pubchem_cid = pubchem_cid

    @property
    def inchi(self):
        return self._inchi

    @inchi.setter
    def inchi(self, inchi):
        self._inchi = inchi

    @property
    def inchi_key(self):
        return self._inchi_key

    @inchi_key.setter
    def inchi_key(self, inchi_key):
        self._inchi_key = inchi_key


def local_run():
    iden = Iden(name="toluene", names="methylbenzene", cas="108-88-3", pubchem_cid=1140, mol_for="C7H8")
    print(iden)


if __name__ == "__main__":
    local_run()
