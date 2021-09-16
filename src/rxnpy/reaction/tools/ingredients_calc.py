from typing import Union
from warnings import warn

from src.rxnpy import Quantity, Unit
from src.rxnpy.chemical.ingredient import Ingredient, IngrRole


DEFAULT_DENSITY = 1 * Unit("g/ml")


class IngrCalculatorError(Exception):
    pass


class QuantityCalculator:
    _error = IngrCalculatorError

    def calc_mass_volume_mole(self, mat: Ingredient):
        if mat.pressure is not None:
            return mat  # nothing to be done with pressure

        if mat.mass is not None:
            if mat.density is not None:
                volume = self._mass_to_volume(mat.mass, mat.density)
                self._approx_same(mat, volume, "volume")
                mat.volume = volume
            if mat.molar_mass is not None:
                mole = self._mass_to_mole(mat.mass, mat.molar_mass)
                self._approx_same(mat, mole, "mole")
                mat.mole = mole

        elif mat.mole is not None:
            if mat.molar_concentration is not None:
                volume = self._mole_to_volume(mat.mole, mat.molar_concentration)
                self._approx_same(mat, volume, "volume")
                mat.volume = volume
            if mat.molar_mass is not None:
                mass = self._mole_to_mass(mat.mole, mat.molar_mass)
                self._approx_same(mat, mass, "mass")
                mat.mass = mass
                if mat.density is not None:
                    volume = self._mass_to_volume(mat.mass, mat.density)
                    self._approx_same(mat, volume, "volume")
                    mat.volume = volume

        elif mat.volume is not None:
            if mat.molar_concentration is not None:
                mole = self._vol_to_mole_conc(mat.volume, mat.molar_concentration)
                self._approx_same(mat, mole, "mole")
                mat.mole = mole
            elif mat.density is not None:
                mass = self._vol_to_mass(mat.volume, mat.density)
                self._approx_same(mat, mass, "mass")
                mat.mass = mass
                if mat.molar_mass is not None:
                    mole = self._mass_to_mole(mat.mass, mat.molar_mass)
                    self._approx_same(mat, mole, "mole")
                    mat.mole = mole

    @staticmethod
    def scale(mat: Ingredient, factor: Union[int, float]):
        if mat.pressure is not None:
            mat.pressure = mat.pressure * factor

        keys = ["mass", "mole", "volume"]
        for k in keys:
            if getattr(mat, k) is not None:
                setattr(mat, k, getattr(mat, k) * factor)

    def _approx_same(self, mat: Ingredient, qty2: Quantity, label: str, error: float = 0.01):
        """Checks if two quantities are approximately the same."""
        if (qty1 := getattr(mat, label)) is None:
            return

        if abs((qty1 - qty2) / qty1) < error:
            return 
        else:
            mes = f"Calculated {label} does not match provided for '{mat.name}'. Calculated: {qty1}," \
                  f" Given by user: {qty2}."
            raise self._error(mes)

    @staticmethod
    def _vol_to_mass(volume: Quantity, density: Quantity) -> Quantity:
        """ Returns mass"""
        return volume * density

    @staticmethod
    def _mass_to_volume(mass: Quantity, density: Quantity) -> Quantity:
        """ Returns volume"""
        return mass / density

    @staticmethod
    def _mass_to_mole(mass: Quantity, molar_mass: Quantity) -> Quantity:
        """ Returns mole"""
        return mass / molar_mass

    @staticmethod
    def _mole_to_mass(mole: Quantity, molar_mass: Quantity) -> Quantity:
        """ Returns mass"""
        return mole * molar_mass

    @staticmethod
    def _vol_to_mole_conc(volume: Quantity, molarity: Quantity) -> Quantity:
        """ Returns moles"""
        return volume * molarity

    @staticmethod
    def _mole_to_volume(mole: Quantity, molarity: Quantity) -> Quantity:
        """ Returns volume"""
        return mole / molarity

    @staticmethod
    def _mole_to_equiv(mole: Quantity, base: Quantity) -> Quantity:
        """ Returns equivalence"""
        return mole / base


class RelativeCalculator:
    _error = IngrCalculatorError

    def calc_equiv_molarity_mass_fraction(self, mats: list[Ingredient], defaults=True):
        """
        Calculates equivalence, molarity and mass fraction if possible
        """
        mats = self._calc_equivalence(mats)
        mats = self._calc_molarity(mats, defaults)
        mats = self._calc_mass_fraction(mats, defaults)

        return mats

    def _calc_equivalence(self, mats: list[Ingredient]):
        """ Calculates molar equivalence for all materials with moles."""
        if not self._check_calc_possible(mats, "mole"):
            return mats

        base = self._get_mole_basis(mats)
        for mat in mats:
            setattr(mat, "equivalence", getattr(mat, "mole") / base)

    @staticmethod
    def _check_calc_possible(mats: list[Ingredient], key: str, required_num: int = 2) -> bool:
        """ Needs at least 2 materials to calculate relative quantities."""
        gas_mat = len([True for mat in mats if mat.pressure is not None])
        adjusted_num = max([2, required_num - gas_mat])
        if len([True for mat in mats if getattr(mat, key) is not None]) >= adjusted_num:
            return True
        else:
            return False

    @staticmethod
    def _get_mole_basis(mats: list[Ingredient]) -> Quantity:
        """
        Returns the moles of base.
        Selection by keyword ordering or first in list if no keywords present.
        """
        base = None
        base_keyword = None
        for mat in mats:
            if mat.mole is not None:
                if base is None:
                    base = mat.mole
                if mat.keyword is not None:
                    if base_keyword is None:
                        base_keyword = mat.keyword
                        base = mat.mole
                    elif mat.keyword < base_keyword:
                        base_keyword = mat.keyword
                        base = mat.mole

        return base

    def _calc_molarity(self, mats: list[Ingredient], default: bool):
        if not self._check_calc_possible(mats, "volume", len(mats)):
            if default:
                pass
            else:
                return mats

        total_volume, mats = self._get_total_volume(mats, default)
        for mat in mats:
            setattr(mat, "molarity", getattr(mat, "mole") / total_volume)

    @staticmethod
    def _get_total_volume(mats: list[Ingredient], default: bool) -> (Quantity, list[Ingredient]):
        total_volume = 0
        mat_not_skipped = []
        for mat in mats:
            if mat.keyword in [IngrRole.WORKUP, IngrRole.QUENCH]:
                continue

            if mat.volume is not None:
                total_volume += mat.volume
                mat_not_skipped.append(mat)
            elif default:
                if mat.mass is not None:
                    total_volume += mat.mass / DEFAULT_DENSITY
                    mat_not_skipped.append(mat)
                    warn(f"Default density used for '{mat.name}' when calculating molarity.")
            else:
                mat_not_skipped.append(mat.name)
                warn(f"'{mat.name}' not included in molarity calculation.")

        return total_volume, mat_not_skipped

    def _calc_mass_fraction(self, mats: list[Ingredient], default: bool):
        if not self._check_calc_possible(mats, "mass", len(mats)):
            if default:
                pass
            else:
                return mats

        total_mass, mats = self._get_total_mass(mats, default)
        for mat in mats:
            setattr(mat, "molarity", getattr(mat, "mass") / total_mass)

    @staticmethod
    def _get_total_mass(mats: list[Ingredient], default: bool) -> (Quantity, list[Ingredient]):
        total_mass = 0
        mat_not_skipped = []
        for mat in mats:
            if mat.keyword in [IngrRole.WORKUP, IngrRole.QUENCH]:
                continue

            if mat.mass is not None:
                total_mass += mat.mass
                mat_not_skipped.append(mat)
            elif default:
                if mat.volume is not None:
                    total_mass += mat.volume * DEFAULT_DENSITY
                    mat_not_skipped.append(mat)
                    warn(f"Default density used for '{mat.name}' when calculating mass fraction.")
            else:
                mat_not_skipped.append(mat.name)
                warn(f"'{mat.name}' not included in mass fraction calculation.")

        return total_mass, mat_not_skipped
