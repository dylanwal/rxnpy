from typing import List, Optional, Union

from rxnpy import Quantity
from rxnpy.chemical.lookup_tools.quantity_parsing.pre_processing import substitution_main, _remove_string
from rxnpy.chemical.lookup_tools.quantity_parsing.multiple_quantity_finder import multiple_quantities_main
from rxnpy.chemical.lookup_tools.quantity_parsing.to_quantity import _to_quantity
from rxnpy.chemical.lookup_tools.quantity_parsing.post_processing import _remove_duplicates


def main_quantity_parse(text_in,
                        remove_string: Optional[List[str]] = None) -> \
        Union[Quantity, List[Quantity], List[List[Quantity]]]:

    if remove_string is not None:
        text_in = _remove_string(text_in, remove_string)

    text_in = substitution_main(text_in)
    text_list = multiple_quantities_main(text_in)

    out = []
    for text in text_list:
        out_inner = []
        for subtext in text:
            result = _to_quantity(subtext)
            if result is not None:
                out_inner.append(result)
        if out_inner:
            out.append(out_inner)

    for _ in range(0, 2):
        if len(out) == 1:
            out = out[0]

    out = _remove_duplicates(out)

    return out


if __name__ == "__main__":
    from testing_utils import _test_func
    examples = [
        ["8.20x10+1 ppm; pure", Quantity("8.20*10**1 ppm")],
        ["37.34 kJ/mole (at 25 °C)", [Quantity("37.34 kJ/mole"), Quantity("25 degC")]],
        ['40 °F (NTP, 1992)', Quantity("40 degF")],
        ['4.0 °C (39.2 °F) - closed cup', [Quantity("4 degC")]],
        ['4.0 °C [39.2 g/[mol * s]] - closed cup', [Quantity("4 degC"), Quantity("39.2 g/(mol * s)")]],
        ['4.0 °C [39.2 g/[mol * s] approx.] - closed cup', [Quantity("4 degC"), Quantity("39.2 g/(mol * s)")]],
        ['4.0 °C [39.2g/[mol*s] approx.] - closed cup', [Quantity("4 degC"), Quantity("39.2 g/(mol * s)")]],
        ['4.0 °C [39.2g/[mol*s]approx.] - closed cup', [Quantity("4 degC"), Quantity("39.2 g/(mol * s)")]],
        ['42.3 gcm-3', Quantity('42.3 g*cm**-3')],
        ['42.3 g cm-3', Quantity('42.3 g*cm**-3')],
        ['40°F', Quantity('40 degF')],
        ['40 °F', Quantity('40 degF')],
        ['115.2-115.3 °C', Quantity('115.2 degC')],
        ['115.2 - 115.3 °C', Quantity('115.2 degC')],
        ['-40 °F', Quantity('-40 degF')],
        ['20.80 mmHg', Quantity('20.80 mmHg')],
        ['18 mm Hg at 68 °F ; 20 mm Hg at 77° F (NTP, 1992)', [[Quantity('18 mmHg'), Quantity('68 degF')],
                                                               [Quantity('20 mmHg'), Quantity('77 degF')]]],
        ['20.8 mm Hg @ 25 °C', [Quantity('20.8 mmHg'), Quantity('25 degC')]],
        ['20.8 mm Hg (25 °C)', [Quantity('20.8 mmHg'), Quantity('25 degC')]],
        ['20.8 mm Hg at 25 °C', [Quantity('20.8 mmHg'), Quantity('25 degC')]],
        ['5e1 g/mol',  Quantity('50 g/mol')],
        ['−66.11·10-62 cm3/mol',  Quantity('-66.11*10**-62 cm**3/mol')],
        ['−66.11·10+62 cm3/mol',  Quantity('-66.11*10**62 cm**3/mol')],
        ['−66.11·1062 cm3/mol', Quantity('-66.11*10**62 cm**3/mol')],
        ['-14.390 BTU/LB= -7992 CAL/G= -334.6X10+5 J/KG', Quantity('-14.390 BTU/lb')],

        ['Sound travels at 0.34 km/s', Quantity('0.34 km/s')],
        ['Pass me a 300 ml beer.', Quantity("300 ml")],

        ['Index of refraction: 1.50920 @ 20 °C/D', [Quantity('1.50920'), Quantity('20 degC')]],
        ['Vapor pressure, kPa at 20 °C: 2.0', [Quantity('2.0 kPa'), Quantity('20 degC')]],
    ]

    delete_text = [
        "approx.",
        "approximate",
        "approx",
        "closed cup",
        "(NTP, 1992)",
        ]

    _test_func(main_quantity_parse, examples, {"remove_string": delete_text})

# 4.0 °C (39.2 °F)  -> -303922.69 kelvin ** 2
