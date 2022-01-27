import os

from pint import UnitRegistry

current_path = os.path.dirname(os.path.realpath(__file__))

u = UnitRegistry(autoconvert_offset_to_baseunit=True,
                 filename=current_path + "\\default_en.txt")
u.default_format = "~"
Quantity = Q = u.Quantity
Unit = U = u.Unit
