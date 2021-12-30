from typing import List, Optional, Any
import re


default_general_substitutions = [
    ["^[a-zA-Z;,.: /]*", ""],  # remove text at front of strings
    ["(?<=[^a-zA-Z])at([^a-zA-Z])", " @ "],  # replace at with @
    ["−", "-"],  # unify dash (long, short) symbols
    ["·", "*"],  # unify multiplication symbols
    ["(?<=[0-9]{1})[ ]{0,1}X[ ]{0,1}(?=[0-9]{1})", "*"],  # unify multiplication symbols
    ["(?<=[0-9]{1})[ ]{0,1}x[ ]{0,1}(?=[0-9]{1})", "*"],  # unify multiplication symbols
    ["\[", "("],  # make all brackets parenthesis
    ["\]", ")"],  # make all brackets parenthesis
    ["={1}.*$", ""],  # if equals in string take first term
    ["^.*:{1}", ""]  # delete everything in front of collen
]


def substitution_main(text_in: List[str]) -> str:
    """Preforms the standard series of substitutions."""
    if isinstance(text_in, list):
        for i, item in enumerate(text_in):
            text_in[i] = _substitution_pipeline(item)
    elif isinstance(text_in, str):
        text_in = _substitution_pipeline(text_in)

    return text_in


def _substitution_pipeline(text_in: str):
    text_in = _substitutions_general(text_in)
    text_in = _substitutions_power(text_in)
    text_in = _substitutions_sci_notation(text_in)
    text_in = _reduce_ranges(text_in)

    return text_in.strip()


def _remove_string(text_in: str, remove_string: List[str]) -> str:
    if isinstance(remove_string, list):
        for text in remove_string:
            text_in = text_in.replace(text, "")

        return text_in.strip()

    raise TypeError(f"Patterns must be a List[List[pattern, substitution]].")


def _substitutions_general(text_in: str,
                           patterns: Optional[List[List[str]]] = default_general_substitutions) -> str:
    """Performs general simple substitutions from list."""
    if isinstance(patterns, list):
        if isinstance(patterns[0], list):
            for pattern in patterns:
                text_in = re.sub(pattern[0], pattern[1], text_in)

            return text_in.strip()

    raise TypeError(f"Patterns must be a List[List[pattern, substitution]].")


def _substitutions_power(text_in: str) -> str:
    """
    replace cm-3 ith cm**-3

    """
    found_unit_power = re.findall("[a-zA-Z]{1,10}[-+]{0,1}[0-4]{1}", text_in)
    for exp in found_unit_power:
        if "-" in exp:
            exp_new = exp.replace("-", "**-", 1)
        elif "+" in exp:
            exp_new = exp.replace("+", "**", 1)
        else:
            exp_new = exp[:-1] + "**" + exp[-1]
        text_in = text_in.replace(exp, exp_new)

    text_in = text_in.replace("e**", "*10**") # to handle  ##e3 to ###e**3
    text_in = text_in.replace("E**", "*10**")  # to handle  ##e3 to ###e**3
    return text_in.strip()


def _substitutions_sci_notation(text_in: str) -> str:
    """
    replace 10-6 with 10**6

    """
    found_sci_notation = re.findall("10[-+]{1}[0-9]{1,5}", text_in)
    for exp in found_sci_notation:
        if "-" in exp:
            exp_new = exp.replace("-", "**-", 1)
        else:
            exp_new = exp.replace("+", "**", 1)
        text_in = text_in.replace(exp, exp_new)

    found_sci_notation = re.findall("[0-9]e[-,+]{0,1}[0-9]{1,5}", text_in)
    for exp in found_sci_notation:
        exp_new = exp.replace("e", "*10**", 1)
        text_in = text_in.replace(exp, exp_new)

    found_sci_notation = re.findall("[0-9]E[-,+]{0,1}[0-9]{1,5}", text_in)
    for exp in found_sci_notation:
        exp_new = exp.replace("E", "*10**", 1)
        text_in = text_in.replace(exp, exp_new)

    found_sci_notation = re.findall("[0-9][* ]{1}10[0-9]{1,5}", text_in)
    for exp in found_sci_notation:
        exp_new = exp.replace("10", "10**", 1)
        text_in = text_in.replace(exp, exp_new)

    return text_in.strip()


def _reduce_ranges(text_in: str) -> str:
    """

    WARNING: Apply _substitutions_sci_notation() first.
    """
    if bool(data_found := re.findall("[-.0-9]{1,6}[- ]{1,3}[-.0-9]{1,6}", text_in)): # match ### - ### or ###-###
        reduced_range = re.findall("[-]{0,1}[.0-9]{1,6}[^0-9-,/; ]{0,8}", data_found[0])[0]
        return text_in.replace(data_found[0], reduced_range)
    else:
        return text_in.strip()


if __name__ == "__main__":
    from testing_utils import _test_func

    test_power = [  # [Input, Output]
        # postive control (makes changes)
        ["42.3 gcm-3", "42.3 gcm**-3"],
        ["66.11·10-62 cm3/mol", "66.11·10-62 cm**3/mol"],
        ["66.11·10-62 cm-3/mol", "66.11·10-62 cm**-3/mol"],
        ["	0.909 g/cm3", "0.909 g/cm**3"],
        ['5.3e1 g/mol', '5.3*10**1 g/mol'],
        ['5.3E1 g/mol', '5.3*10**1 g/mol'],

        # negative control (no changes made)
        ["40 °F", "40 °F"],
        ["39.2 g/[mol * s]]", "39.2 g/[mol * s]]"],
        ['-14.390 BTU/LB= -7992 CAL/G= -334.6*10+5 J/KG', '-14.390 BTU/LB= -7992 CAL/G= -334.6*10+5 J/KG']
    ]
    _test_func(_substitutions_power, test_power)


    test_sci_notation = [  # [Input, Output]
        # postive control (makes changes)
        ["66.11·10-62 cm3/mol", "66.11·10**-62 cm3/mol"],
        ["66.11·10-62 cm-3/mol", "66.11·10**-62 cm-3/mol"],
        ['-14.390 BTU/LB= -7992 CAL/G= -334.6*10**5 J/KG', '-14.390 BTU/LB= -7992 CAL/G= -334.6*10**5 J/KG'],
        ["	0.909 g/cm3", "0.909 g/cm3"],
        ['5.3e1 g/mol', '5.3*10**1 g/mol'],
        ['5.3E1 g/mol', '5.3*10**1 g/mol'],

        # negative control (no changes made)
        ['5.3*10**1 g/mol', '5.3*10**1 g/mol'],
        ["42.3 gcm-3", "42.3 gcm-3"],
        ["0.909 g/cm3", "0.909 g/cm3"],
        ["40 °F", "40 °F"],
        ["39.2 g/[mol * s]]", "39.2 g/[mol * s]]"],
    ]
    _test_func(_substitutions_sci_notation, test_sci_notation)


    test_reduce_ranges = [  # [Input, Output]
        # postive control (makes changes)
        ['115.2-115.3 °C', '115.2 °C'],
        ['115.2 - 115.3 °C', '115.2 °C'],
        ["	0.909 g/cm3", "0.909 g/cm3"],

        # negative control (no changes made)
        ["66.11·10**-62 cm-3/mol", "66.11·10**-62 cm-3/mol"],
        ['-14.390 BTU/LB= -7992 CAL/G= -334.6*10**5 J/KG', '-14.390 BTU/LB= -7992 CAL/G= -334.6*10**5 J/KG'],
        ["42.3 gcm-3", "42.3 gcm-3"],
        ["0.909 g/cm3", "0.909 g/cm3"],
        ["40 °F", "40 °F"],
        ["39.2 g/[mol * s]]", "39.2 g/[mol * s]]"],
    ]
    _test_func(_reduce_ranges, test_reduce_ranges)


    test_sub_pattern1 = [
        # postive control (makes changes)
        ['Pass me a 300 ml beer.', '300 ml beer.'],
        ["	0.909 g/cm3", "0.909 g/cm3"],
        ['Sound travels at 0.34 km/s', '0.34 km/s'],

        # negative control (no changes made)
        ["42.3 gcm-3", "42.3 gcm-3"],
        ["40 °F", "40 °F"],
        ["39.2 g/[mol * s]]", "39.2 g/[mol * s]]"],
        ['−66.11·10-62 cm3/mol', '−66.11·10-62 cm3/mol']
    ]
    pattern = ["^[a-zA-Z;,.: /]*", ""]
    print(f"\nTest pattern: '{pattern[0]}' -> '{pattern[1]}'")
    _test_func(_substitutions_general, test_sub_pattern1, {"patterns": [pattern]})


    test_sub_pattern2 = [
        # positive control (makes changes)
        ["37.34 kJ/mole (at 25 °C)", "37.34 kJ/mole ( @ 25 °C)"],
        ['20.8 mm Hg at 25 °C', '20.8 mm Hg  @ 25 °C'],
        ["	0.909 g/cm3", "0.909 g/cm3"],
        ['Sound travels at 0.34 km/s', 'Sound travels  @ 0.34 km/s'],

        # negative control (no changes made)
        ['20.8 mm Hg @ 25 °C', '20.8 mm Hg @ 25 °C'],
        ['20.8 mm Hgat25 °C', '20.8 mm Hgat25 °C'],
        ['Pass me a 300 ml beer.', 'Pass me a 300 ml beer.'],
        ["42.3 gcm-3", "42.3 gcm-3"],
        ["40 °F", "40 °F"],
        ["39.2 g/[mol * s]]", "39.2 g/[mol * s]]"],
        ['−66.11·10-62 cm3/mol', '−66.11·10-62 cm3/mol']
    ]
    pattern = ["(?<=[^a-zA-Z])at([^a-zA-Z])", " @ "]
    print(f"\nTest pattern: '{pattern[0]}' -> '{pattern[1]}'")
    _test_func(_substitutions_general, test_sub_pattern2, {"patterns": [pattern]})


    test_sub_pattern3 = [
        # postive control (makes changes)
        ['-14.390 BTU/LB= -7992 CAL/G= -334.6X10+5 J/KG', '-14.390 BTU/LB'],
        ["	0.909 g/cm3", "0.909 g/cm3"],

        # negative control (no changes made)
        ['Sound travels at 0.34 km/s', 'Sound travels at 0.34 km/s'],
        ['20.8 mm Hg @ 25 °C', '20.8 mm Hg @ 25 °C'],
        ['20.8 mm Hgat25 °C', '20.8 mm Hgat25 °C'],
        ['Pass me a 300 ml beer.', 'Pass me a 300 ml beer.'],
        ["42.3 gcm-3", "42.3 gcm-3"],
        ["40 °F", "40 °F"],
        ["39.2 g/[mol * s]]", "39.2 g/[mol * s]]"],
        ['−66.11·10-62 cm3/mol', '−66.11·10-62 cm3/mol']
    ]
    pattern = ["={1}.*$", ""]
    print(f"\nTest pattern: '{pattern[0]}' -> '{pattern[1]}'")
    _test_func(_substitutions_general,test_sub_pattern3, {"patterns": [pattern]})


    test_sub_pattern3 = [
        # postive control (makes changes)
        ['Sound travels: 0.34 km/s', '0.34 km/s'],

        # negative control (no changes made)
        ['Sound travels at 0.34 km/s', 'Sound travels at 0.34 km/s'],
        ['20.8 mm Hg @ 25 °C', '20.8 mm Hg @ 25 °C'],
        ['20.8 mm Hgat25 °C', '20.8 mm Hgat25 °C'],
        ['Pass me a 300 ml beer.', 'Pass me a 300 ml beer.'],
        ["42.3 gcm-3", "42.3 gcm-3"],
        ["40 °F", "40 °F"],
        ["39.2 g/[mol * s]]", "39.2 g/[mol * s]]"],
        ['−66.11·10-62 cm3/mol', '−66.11·10-62 cm3/mol']
    ]
    pattern = ["^.*:{1}", ""]
    print(f"\nTest pattern: '{pattern[0]}' -> '{pattern[1]}'")
    _test_func(_substitutions_general,test_sub_pattern3, {"patterns": [pattern]})