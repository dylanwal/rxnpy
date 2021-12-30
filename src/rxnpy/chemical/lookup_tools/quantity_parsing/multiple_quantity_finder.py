from typing import List, Union
from warnings import warn
import re

from rxnpy import Unit


def multiple_quantities_main(text_in):
    text_list = _multiple_quantities(text_in)
    out = []
    for text in text_list:
        out.append(_condition_finder(text))

    return out


def _multiple_quantities(text_in: str) -> List[str]:
    result = re.split(";", text_in)
    return [text.strip() for text in result]


def _condition_finder(text_in: str) -> List[str]:
    """
    Extracts conditions and creates list [quantity, conditions]

    Warning: replace 'at' with '@' first (use _substitutions_general in pre_processing.py)
    """
    if isinstance(text_in, str):
        text_list = [text_in]
    elif isinstance(text_in, list):
        text_list = text_in
    else:
        raise TypeError("Only str and List[str] allowed.")

    out = []
    for text in text_list:
        if "(" in text and ")" in text:
            _out = _remove_one_layer_parenthesis(text)
            if isinstance(_out, str):
                out.append(_out)
            else:
                out += _out
        elif "(" in text or ")" in text:
            out += text.replace("(", "").replace(")", "")
        else:
            out.append(text)

    out2 = []
    for text in out:
        if "@" in text:
            result = re.split("@", text)
            out2 += [t.strip() for t in result]
        else:
            out2.append(text)

    return [text.strip() for text in out2]


def _remove_one_layer_parenthesis(text_in: str) -> Union[List[str], str]:
    """ Removes one layer of parenthesis."""
    if "(" not in text_in and ")" not in text_in:
        return text_in

    text_in = text_in.strip()

    start_index = None
    counter_open = 0
    counter_close = 0
    end_index = None
    early_finish_flag = False
    for i, letter in enumerate(text_in):
        if start_index is None and letter == "(":
            start_index = i
            counter_open += 1
        elif start_index is not None and letter == "(":
            counter_open += 1
        elif counter_open == 1 and letter == ")":
            counter_close += 1
            end_index = i
            early_finish_flag = True
            break
        elif letter == ")":
            counter_close += 1
            end_index = i

    if counter_open is None or counter_close is None or counter_open != counter_close:
        warn(f"\nUnbalanced parenthesis. Openings '(':{counter_open} ; Closings ')': {counter_close}.")
        return text_in

    if start_index == 0 and end_index == len(text_in)-1:   # "(####)"
        return text_in[1:end_index]
    elif start_index != 0 and end_index == len(text_in)-1:  # "#####(####)"
        try:
            Unit(text_in[start_index+1:-1])
            return text_in
        except Exception:
            pass
        return [text_in[0:start_index], text_in[start_index+1:-1]]
    elif start_index == 0 and end_index != len(text_in)-1:  # "(####)#####"
        out = [text_in[1:end_index], text_in[end_index+1:]]
        try:
            Unit(out[0])
            return text_in
        except Exception:
            pass
        if early_finish_flag:
            _out = _remove_one_layer_parenthesis(out.pop(1))
            if isinstance(_out, str):
                out.append(_out)
            else:
                out += _out
            return out
    elif start_index != 0 and end_index != len(text_in)-1:  # "#####(####)####"
        out = [text_in[0:start_index], text_in[start_index+1:end_index], text_in[end_index+1:]]
        try:
            Unit(out[1])
            return text_in
        except Exception:
            pass
        if early_finish_flag:
            _out = _remove_one_layer_parenthesis(out.pop(2))
            if isinstance(_out, str):
                out.append(_out)
            else:
                out += _out
            return out


if __name__ == "__main__":
    from testing_utils import _test_func
    test_multiple_quantities = [  # [Input, Output]
        # positive control (works)
        ['18 mm Hg at 68 °F ; 20 mm Hg at 77° F', ['18 mm Hg at 68 °F', '20 mm Hg at 77° F']],
        ['18 mm Hg @ 68 °F ; 20 mm Hg @ 77° F (NTP, 1992)', ['18 mm Hg @ 68 °F', '20 mm Hg @ 77° F (NTP, 1992)']],

        # negative control (fails)
        ['20.8 mm Hg @ 25 °C', ['20.8 mm Hg @ 25 °C']],
        ['20.8 mm Hgat25 °C', ['20.8 mm Hgat25 °C']],
        ['Pass me a 300 ml beer.', ['Pass me a 300 ml beer.']],
        ["42.3 gcm-3", ["42.3 gcm-3"]],
        ["40 °F", ["40 °F"]],
        ["39.2 g/[mol * s]]", ["39.2 g/[mol * s]]"]],
        ['−66.11·10-62 cm3/mol', ['−66.11·10-62 cm3/mol']]
    ]
    _test_func(_multiple_quantities, test_multiple_quantities)


    test_condition_finder = [  # [Input, Output]
        # # positive control (works)
        ['18 mm Hg @ 68 °F ', ['18 mm Hg', '68 °F']],
        ['20 mm Hg @ 77° F', ['20 mm Hg', '77° F']],
        [' 20 mm Hg @ 77° F (NTP, 1992)', ['20 mm Hg', '77° F', 'NTP, 1992']],

        ['40 °F (4 °C) (Closed cup)', ['40 °F', '4 °C', 'Closed cup']],
        ['40 °F (4 °C)', ['40 °F', '4 °C']],
        ['40 °F (Closed cup)', ['40 °F', 'Closed cup']],
        ['40 °F(Closed cup)', ['40 °F', 'Closed cup']],
        ['40 °F ((4 °C) Closed cup)', ['40 °F', '(4 °C) Closed cup']],
        ['((4 °C) Closed cup)', ['(4 °C) Closed cup']],
        ['(4 °C Closed cup)', ['4 °C Closed cup']],

        # negative control (fails)
        ['20.8 mm Hg 25 °C', ['20.8 mm Hg 25 °C']],
        ['20.8 mm Hgat25 °C', ['20.8 mm Hgat25 °C']],
        ['Pass me a 300 ml beer.', ['Pass me a 300 ml beer.']],
        ["42.3 gcm-3", ["42.3 gcm-3"]],
        ["40 °F", ["40 °F"]],
        ["39.2 g/[mol * s]]", ["39.2 g/[mol * s]]"]],
        ['−66.11·10-62 cm3/mol', ['−66.11·10-62 cm3/mol']],

        ['40 g/(mol s)', ['40 g/(mol s)']],
    ]
    _test_func(_condition_finder, test_condition_finder)


    examples = [  # [Input, Output]
        # positive control (works)
        ["(aaaaa)", "aaaaa"],
        ["(aa(a)aa)", "aa(a)aa"],
        ["(aaa)(aa)", ["aaa", "aa"]],
        ["aaa(aa)", ["aaa", "aa"]],
        ["(aaaaa))", ["aaaaa", ")"]],

        # negative control (fails)
        ["(aaaaa", "(aaaaa"],
        ["(aa(aaa)", "(aa(aaa)"],
    ]
    _test_func(_remove_one_layer_parenthesis, examples)
