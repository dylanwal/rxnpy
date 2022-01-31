from typing import Union
import pprint

from dictpy import Serializer

from rxnpy.utilities.decorators import freeze_class
from rxnpy.utilities.reference_list import ObjList
from rxnpy.chemical.sub_objects.identifiers import Iden
from rxnpy.chemical.sub_objects.logger import logger_chem
from rxnpy.chemical.sub_objects.property import Prop


@freeze_class
class Chemical(Serializer):
    _logger = logger_chem

    def __init__(self,
                 iden: Iden,
                 prop: Union[list[Prop], Prop] = None,
                 ):
        self.iden = iden
        self.prop = ObjList(Prop, prop, _logger=self._logger)

    def __repr__(self):
        text = repr(self.iden)
        text += f"; # of props = {len(self.prop)}"
        return text

    def pprint(self):
        dict_out = self.remove_none(self.dict_cleanup(self.as_dict()))
        return pprint.pprint(dict_out)

    @staticmethod
    def load(dict_: dict):
        if "iden" not in dict_:
            raise ValueError("'iden' must in dictionary.")
        chemical = Chemical(iden=Iden(**dict_["iden"]))

        if "prop" in dict_:
            for prop in dict_["prop"]:
                p = Prop.load(prop)
                chemical.prop.add(p)

        return chemical


def local_run():
    from rxnpy import Q
    from rxnpy.chemical.sub_objects.condition import Cond

    iden = Iden(name="toluene", names="methylbenzene", cas="108-88-3", pubchem_cid=1140, mol_for="C7H8")

    chemical = Chemical(iden,
                        [
                            Prop("temp_boil", Q("111 degC")),
                            Prop("molar_mass", Q("92.1 g/mol")),
                            Prop("density", Q("0.87"), cond=Cond("temp", Q("20 degC")))
                        ])

    print(chemical)
    json_ = chemical.to_JSON()
    pprint.pprint(json_)


if __name__ == "__main__":
    local_run()
