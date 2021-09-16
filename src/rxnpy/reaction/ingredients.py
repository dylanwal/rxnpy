from warnings import warn


from src.rxnpy.chemical.ingredient import Ingredient
from src.rxnpy.reaction.tools.ingredients_calc import QuantityCalculator, RelativeCalculator


class IngredientsError(Exception):
    pass


class Ingredients:
    _error = IngredientsError
    _label_length = 12

    def __init__(self, *args):
        """
        Functions: add, remove, scale, scale_one
        __init__ calls add

        :param see add function
        """

        self._ingrs = []
        self._init_with_args(*args)

    def __repr__(self):
        return self._table()

    def __str__(self):
        return self._table()

    def __call__(self):
        return self._ingr

    def __len__(self):
        return len(self._ingr)

    def __getitem__(self, item):
        index = self._get_mat_index(item)
        return self._ingr[index]

    def _init_with_args(self, *args):
        if args:
            for arg in args[0]:
                # get keyword arguments
                kwarg = {}
                for i, a in enumerate(arg):
                    if isinstance(a, dict) and len(a.keys()) == 1:
                        kwarg = kwarg | arg.pop(i)

                try:
                    self.add(*arg, **kwarg)
                except TypeError as e:
                    warn(f"Material skipped: '{arg}'. {e}")

    def add(self, ingr: Ingredient, equivalence: list[Union[float, int], Union[int, str]] = None):
        """
        Adds mat to Ingr and performs calculations for the other quantities.
        :param mat:
        :param equivalence: [equivalence, "material"] "material" is the equivalence is in respect to
        """
        if equivalence is not None:
            index = self._get_mat_index(equivalence[1])
            ingr["mole"] = self._ingr[index]["mole"] * equivalence[0]

        self._ingr.append(self._q_calc.calc_mass_volume_mole(mat))
        self._ingr = self._r_calc.calc_equiv_molarity_mass_fraction(self._ingr)

    def remove(self, mat: Union[int, str]):
        """
        Removes mat from ingr
        :param mat: material to be removed
        """
        if isinstance(mat, int) and mat <= len(self._ingr):
            del self._ingr[mat]
        elif isinstance(mat, str):
            mat = self._get_mat_index(mat)
            del self._ingr[mat]
        else:
            mes = f"'{mat}' invalid input."
            raise self._error(mes)

        self._ingr = self._r_calc.calc_equiv_molarity_mass_fraction(self._ingr)

    def scale(self, factor: Union[int, float]):
        """
        Scales all ingredients' mass, volume, moles by a factor.
        :param factor: scale factor
        """
        for i in range(len(self._ingr)):
            self._ingr[i] = self._q_calc.scale(self._ingr[i], factor)

    def scale_one(self, mat: Union[int, str], factor: Union[int, float]):
        """
        Scales one ingredient's mass, volume, moles by a factor.
        :param mat: material to be scaled
        :param factor: scale factor
        """
        index = self._get_mat_index(mat)

        self._ingr[index] = self._q_calc.scale(self._ingr[index], factor)
        self._ingr = self._r_calc.calc_equiv_molarity_mass_fraction(self._ingr)

    def _get_mat_index(self, target: Union[str, int]):
        if isinstance(target, int):
            if target <= len(self._ingr):
                return target

        possible_names = [i["name"] for i in self._ingr]
        scores = {v: SequenceMatcher(None, target, v).ratio() * 100 for v in possible_names}
        best_match = max(scores, key=scores.get)
        best_score = scores[best_match]
        if best_score < 75:
            mes = f"No match to '{target}' found in ingredients. Try a different writing of the chemical name."
            raise self._error(mes)

        return possible_names.index(best_match)

    def _table(self) -> str:
        """
        Creates a nice viewable table.
        """
        if len(self._ingr) == 0:
            return "No ingredients."

        headers, units = self._table_headers()
        headers.insert(0, "#")
        units.insert(0, "")
        row_format = "{:<3}" + ("{:<" + str(self._label_length) + "}") * (len(headers) - 1)
        text_out = row_format.format(*[self._length_limit_header(h) for h in headers])
        text_out += "\n" + row_format.format(*[f"({u})" if u != "" else "" for u in units])
        text_out += "\n" + "-" * self._label_length * len(headers)
        for i, ingr in enumerate(self._ingr):
            entries = []
            for k, u in zip(headers, units):
                if k in ingr.keys():
                    v = ingr[k]
                    if u != "":
                        value = self.sig_figs(v.to(u).m)
                    elif isinstance(v, Quantity):
                        value = self.sig_figs(v.to_base_units().m)
                    else:
                        value = str(v)
                    entries.append(self._length_limit_header(value))
                elif k == "#":
                    entries.append(f"{i}")
                else:
                    entries.append("---")

            text_out += "\n" + row_format.format(*entries)

        text_out += "\n" * 2
        return text_out

    def _table_headers(self):
        headers = []
        back_headers = []
        units = []
        back_units = []
        divide = 0
        divide2 = 0
        for ingr in self._ingr:
            for k in ingr.keys():
                if k not in headers + back_headers:
                    if k == "name":
                        headers.insert(0, k)
                        units.insert(0, "")
                        divide += 1
                    elif k in self._q_calc.keys_qty.keys():
                        headers.insert(divide, k)
                        units.insert(divide, self._q_calc.keys_qty[k]["unit"])
                        divide += 1
                    elif k in self._q_calc.keys_rel.keys():
                        headers.insert(divide + divide2, k)
                        units.insert(divide + divide2, self._q_calc.keys_rel[k]["unit"])
                        divide2 += 1
                    elif k in self._q_calc.keys_calc.keys():
                        headers.insert(divide + divide2 + 1, k)
                        units.insert(divide + divide2 + 1, self._q_calc.keys_calc[k]["unit"])
                    else:
                        back_headers.append(k)
                        back_units.append("")

        return headers + back_headers, units + back_units

    def _length_limit_header(self, entry) -> str:
        length_limit = self._label_length
        if len(entry) > length_limit:
            return entry[0:length_limit - 2]

        return entry

    @staticmethod
    def sig_figs(number: float, significant_figures: int = 3) -> str:
        """
        Given a number return a string rounded to the desired significant digits.
        :param number:
        :param significant_figures:
        :return:
        """
        try:
            return '{:g}'.format(float('{:.{p}g}'.format(number, p=significant_figures)))
        except Exception:
            return str(number)

if __name__ == "__main__":
    calc = IngredientCalculator()
    calc.add({
        "name": "secbuLi",
        "volume": 0.0172 * Unit("ml"),
        "molar_mass": 64.06 * Unit("g/mol"),
        "density": 0.768 * Unit("g/ml"),
        "molar_conc": 1.3 * Unit("M")
    })
    calc.add({
        "name": "styrene",
        "mass": 0.455 * Unit("g"),
        "molar_mass": 104.15 * Unit("g/mol"),
        "density": 0.909 * Unit("g/ml")
    })
    calc.add({
        "name": "toluene",
        "volume": 10 * Unit("ml"),
        "molar_mass": 92.141 * Unit("g/mol"),
        "density": 0.87 * Unit("g/ml")
    })
    calc.add({
        "name": "THF",
        "mole": 45.545 * Unit("mmol"),
        "molar_mass": 72.107 * Unit("g/mol"),
        "density": .8876 * Unit("g/ml"),
    })
    print(calc)
    calc.scale(2)
    print(calc)
    calc.remove("toluene")
    print(calc)
    calc.scale_one("styrene", 0.5)
    print(calc)
