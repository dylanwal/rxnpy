import sys

from rxnpy.config.quantity import Quantity

float_limit = sys.float_info.max

cond_keys = {
    "time": {
        "type": Quantity,
        "range": [0, float_limit],
        "unit": "second",
        "unit_prefer": "min",
        "descr": "Time"
    },
    "temp": {
        "type":  Quantity,
        "range": [0, float_limit],
        "unit": "kelvin",
        "unit_prefer": "degC",
        "descr": "Temperature"
    },
    "pres": {
        "type":  Quantity,
        "range": [0, float_limit],
        "unit": "kilogram / meter / second ** 2",
        "unit_prefer": "kPa",
        "descr": "Absolute pressure"
    },
    "light_power": {
        "type":  Quantity,
        "range": [0, float_limit],
        "unit": "kilogram * meter ** 2 / second ** 3",
        "unit_prefer": "watt",
        "descr": "Light power hitting a surface (Not electrical power)"
    },
    "light_power_e": {
        "type":  Quantity,
        "range": [0, float_limit],
        "unit": "kilogram * meter ** 2 / second ** 3",
        "unit_prefer": "watt",
        "descr": "Electric power driving the light"
    },
    "light_irradiance": {
        "type":  Quantity,
        "range": [0, float_limit],
        "unit": "kilogram / second ** 3",
        "unit_prefer": "mW/cm**2",
        "descr": "Light power per area"
    },
    "light_wlength": {
        "type":  Quantity,
        "range": [0, float_limit],
        "unit": "meter",
        "unit_prefer": "nm",
        "descr": "max wave length of light"
    },
    "stirring": {
        "type": float,
        "range": [0, float_limit],
        "unit": "radian / second",
        "unit_prefer": "rpm",
        "descr": "rate of stirrer"
    },
    "potential": {
        "type":  Quantity,
        "range": [0, float_limit],
        "unit": "kilogram * meter ** 2 / ampere / second ** 3",
        "unit_prefer": "V",
        "descr": "electrical potential"
    }
}
