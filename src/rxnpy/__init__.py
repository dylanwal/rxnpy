import sys
from pint import UnitRegistry
import os


current_path = os.path.dirname(os.path.realpath(__file__))


u = UnitRegistry(autoconvert_offset_to_baseunit=True, filename=os.path.join(current_path, "default_en.txt"))
Quantity = u.Quantity
Unit = u.Unit

float_limit = sys.float_info.max
