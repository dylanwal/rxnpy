from typing import List, Optional, Any, Union, Tuple
import re

from rxnpy import Unit, Quantity
from rxnpy.chemical.lookup_tools.quantity_parsing.sig_figs import sig_figs
from rxnpy.chemical.lookup_tools.quantity_parsing.pre_processing import _substitutions_general
from rxnpy.chemical.lookup_tools.quantity_parsing.utils import _flatten_list, _contains_number


last_minute_substitions = [
    ["LB", "lb"],
    ["mm Hg", "mmHg"],
    ["kpa", "kPa"],
    ["-{1}[^0-9]*$", ""],
    ["° F", "°F"],
    ["° C", "°C"],
]


def _to_quantity(text_in: str) -> Quantity:
    """Attempt to create Quantity from string."""
    text_in = _substitutions_general(text_in, last_minute_substitions)
    if "@" in text_in:
        return None
    if not _contains_number(text_in):
        return None

    try:
        return Quantity(text_in)
    except Exception:
        return _to_quantity_expanded(text_in)


def _to_quantity_expanded(text_in: str) -> Quantity:
    """Attempt to create Quantity from string stepwise process."""
    value, text_value = _get_value(text_in)
    if value is None:
        return None

    unit = _get_unit(re.sub(text_value, "", text_in))
    if unit is None:
        return None

    return value * unit


def _get_value(text_in: str) -> Tuple[Union[float, int], str]:
    """Extracts value out of string. Value must be at the start of string."""
    try:
        result = re.findall('^[-]{0,1}[0-9.]+[*]{0,1}[0-9.]*[*]{0,2}[-]{0,1}[0-9.]*', text_in.lstrip())[0]
        return sig_figs(eval(result, {'__builtins__': None}), significant_digit=15), result
    except IndexError:
        return None, None


def _get_unit(text_in: str) -> Unit:
    if text_in is None:
        return None
    if text_in == "":
        return Unit("")
    if bool(re.findall("^[ ]*[-0-9].", text_in)):
        return None

    split_text = _split_on_parenthesis(text_in)
    split_text = _split_on_powers(split_text)
    split_text = _split_on_multiplication_symbol(split_text)
    split_text = _split_on_division_symbol(split_text)

    if isinstance(split_text, Unit):
        return split_text

    split_text = _split_list(split_text, " ", maxsplit=10)

    if isinstance(split_text, list) and len(split_text) == 1 and isinstance(split_text[0], Unit):
        return split_text[0]

    split_text = [chunk for chunk in split_text if (isinstance(chunk, str) and chunk != " ")]
    split_text = [chunk for chunk in split_text if chunk != ""]

    for i, chunk in enumerate(split_text):
        if not isinstance(chunk, Unit):
            try:
                split_text[i] = Unit(chunk)
            except Exception:
                result = _frame_shift(chunk)
                split_text[i] = result

    split_text = [chunk for chunk in split_text if chunk is not None]

    if split_text == []:
        return None

    if not all([isinstance(i, Unit) for i in split_text]):
        return None

    out = split_text[0]
    for i in split_text[1:]:
        out = out * i

    return out


def _split_on_multiplication_symbol(text_in: Union[str, list[str]]) -> List[str]:
    """Splits text up into a list of strings based on *"""
    if isinstance(text_in, list):
        if None in text_in:
            return text_in
        text_list = text_in
    elif isinstance(text_in, str):
        text_list = [text_in]
    else:
        return text_in

    for i, text in enumerate(text_list):
        if isinstance(text, str) and "*" in text:
            new_splits = re.split("([^*]+)[ ]{0,1}[*]{1}[ ]{0,1}([^*-0-9].*)", text)
            if len(new_splits) > 1:
                new_splits = [chunk for chunk in new_splits if chunk != ""]
                for ii, split in enumerate(new_splits):
                    if "*" in split:
                        new_splits[ii] = _split_on_multiplication_symbol(split)

                text_list[i] = new_splits
                continue
            else:
                if text[-1] == "*":
                    text_list[i] = text[:-1]

    return _flatten_list(text_list)


def _split_on_division_symbol(text_in: Union[str, list[str]]) -> List[str]:
    """Splits text up into a list of strings based on /"""
    if isinstance(text_in, list):
        if None in text_in:
            return text_in
        text_list = text_in
    elif isinstance(text_in, str):
        text_list = [text_in]
    else:
        return text_in

    FLAG = False
    for i, text in enumerate(text_list):
        if isinstance(text, str) and "/" in text:
            new_splits = re.split("([/]{1})", text)
            new_splits = [chunk for chunk in new_splits if chunk != ""]

            if FLAG:
                previous_value = text_list[i-1]
                if isinstance(previous_value, Unit):
                    previous_value = _get_unit(previous_value)
                if new_splits[0] != "":
                    new_splits[0] = _get_unit(new_splits[0])
                else:
                    return None
                if isinstance(previous_value, Unit) and isinstance(new_splits[0], Unit):
                    new_splits[0] = previous_value / new_splits[0]
                    text_list[i - 1] = ""
                    FLAG = False
                else:
                    return None

            if len(new_splits) == 3:
                new_splits[0] = _get_unit(new_splits[0])
                new_splits[2] = _get_unit(new_splits[2])
                if isinstance(new_splits[0], Unit) and isinstance(new_splits[2], Unit):
                    text_list[i] = new_splits[0] / new_splits[2]
                else:
                    return None

            elif len(new_splits) == 2 and new_splits[0] == "/":
                previous_value = text_list[i-1]
                if isinstance(previous_value, Unit):
                    previous_value = _get_unit(previous_value)
                new_splits[1] = _get_unit(new_splits[1])
                if isinstance(previous_value, Unit) and isinstance(new_splits[1], Unit):
                    text_list[i] = previous_value / new_splits[1]
                    text_list[i - 1] = ""
                else:
                    return None

            elif len(new_splits) == 2 and new_splits[1] == "/":
                FLAG = True
                text_list[i] = new_splits[0]
                continue

        if FLAG:
            previous_value = text_list[i - 1]
            if not isinstance(previous_value, Unit):
                previous_value = _get_unit(previous_value)
            if not isinstance(text, Unit):
                text = _get_unit(text)
            if isinstance(previous_value, Unit) and isinstance(text, Unit):
                text_list[i] = previous_value / text
                text_list[i - 1] = ""
                FLAG = False
            else:
                return None

    return [text for text in _flatten_list(text_list) if text != ""]


def _split_on_parenthesis(text_in: Union[str, list[str]]) -> List[str]:
    """Splits text up into a list of strings based on parenthesis locations."""
    if isinstance(text_in, list):
        if None in text_in:
            return text_in
        text_list = text_in
    elif isinstance(text_in, str):
        text_list = [text_in]
    else:
        return text_in

    for i, text in enumerate(text_list):
        if isinstance(text, str) and "(" in text:
            text_inside = text[text.find("(")+1:text.rfind(")")]
            out_add = _split_list(text, text_inside)
            out_add[0] = out_add[0][:-1]  # remove (
            out_add[2] = out_add[2][1:]  # remove )
            out_add[1] = _get_unit(text_inside)

            out_add = [text for text in out_add if text != ""]
            out_add = [text for text in out_add if text != None]
            text_list[i] = out_add

    return _flatten_list(text_list)


def _split_on_powers(text_in: Union[str, list[str]]) -> List[str]:
    """Splits text up into a list of strings based on ** locations."""
    if isinstance(text_in, list):
        if None in text_in:
            return text_in
        text_list = text_in
    elif isinstance(text_in, str):
        text_list = [text_in]
    else:
        return text_in

    for i, text in enumerate(text_list):
        out_add = []
        if isinstance(text, str) and "**" in text:
            out_add = re.split("([a-zA-Z]+[ ]{0,1}[*]{2}[ ]{0,1}[-+]{0,1}[0-9]+)", text, maxsplit=1)
            try:
                out_add[1] = Unit(out_add[1])
            except Exception:
                pass

            if "**" in out_add[2]:
                last_term = out_add.pop(2)
                out_add += _split_on_powers(last_term)

            text_list[i] = [text for text in out_add if text != ""]

    # text_split = text_in_list
    # for text_ in text_in_list:
    #     if isinstance(text_, str) and "**" in text_:
    #         power_chunks = re.findall("[a-zA-Z]+[ ]{0,1}[*]{2}[ ]{0,1}[-+]{0,1}[0-9]+", text_)
    #         for chunk in power_chunks:
    #             text_split = _split_list(text_split, chunk)
    #
    #             # Turn parenthesis into a Unit if valid
    #             unit_ = _get_unit(chunk)
    #
    #             for i, obj in enumerate(text_split):
    #                 if obj == chunk:
    #                     text_split[i] = unit_
    return _flatten_list(text_list)


def _split_list(text_split: List[Union[str, Any]], chunks: Union[str, List[str]], maxsplit: int = 1) \
        -> List[Union[str, Any]]:
    """Splits text up into a list of strings based on chunks."""
    if isinstance(chunks, str):
        chunks = [chunks]
    if isinstance(text_split, str):
        text_split = [text_split]
    if not isinstance(text_split, list):
        return text_split

    for chunk in chunks:
        for i, text in enumerate(text_split):
            if isinstance(text, str) and chunk in text:
                split_cell = text_split.pop(i).split(chunk, maxsplit=maxsplit)  # split cell into 2
                split_cell.insert(1, chunk)  # insert chunk back into middle
                split_cell = [cell for cell in split_cell if cell]  # remove empty strings ""
                for ii, cell in enumerate(split_cell):  # re-add the new split cells back into list in the correct position
                    text_split.insert(i+ii, cell)
                break

    return text_split


def _merge_split_text(split_text: List[Union[str, Unit]])-> Unit:
    unit_out = None
    skip_flag = False
    for i, chunk in split_text:
        if isinstance(chunk, Unit):
            if unit_out is None:
                unit_out = chunk
            else:
                unit_out = unit_out * chunk
        elif chunk == "/":
            pass


def _frame_shift(text_in: str) -> Unit:
    """

    Warning: "/" should not be in text
    """
    _frame_dict = {}
    for set_size in range(1, 9):
        for i in range(len(text_in)):
            upper_bound = i + set_size
            if upper_bound > len(text_in):
                break

            text = text_in[i: i+set_size]
            try:
                unit_ = Unit(text)
                _frame_dict[text] = {
                    "set_size": set_size,
                    "unit": unit_,
                    "bounds": [i, i+set_size]
                }
            except Exception:
                unit_ = None

    if _frame_dict == {}:
        return None

    replace = {}
    for i in range(10):
        # get max frame
        max_value = 0
        max_key = ""
        for  k, v in _frame_dict.items():
            if v["set_size"] > max_value:
                max_value =  v["set_size"]
                max_key = k

        replace[max_key] = _frame_dict.pop(max_key)

        remove_keys = []
        for k, v in _frame_dict.items():
            if replace[max_key]["bounds"][0] <= v["bounds"][0] < replace[max_key]["bounds"][1] or \
                replace[max_key]["bounds"][0] < v["bounds"][1] <= replace[max_key]["bounds"][1]:
                remove_keys.append(k)

        for k in remove_keys:
            _frame_dict.pop(k)

        if not _frame_dict:
            break # dictionary is empty

    # Taking "replace" and "text in" and merging
    count_list = list(range(0, len(text_in), 1))
    compile_list = []
    for i in range(0, len(text_in)):
        int_ = count_list[0]
        for v in replace.values():
            if v["bounds"][0] <= int_ < v["bounds"][1]:
                compile_list.append(v["unit"])
                remove_num = range(v["bounds"][0], v["bounds"][1])
                for num in remove_num:
                    count_list.remove(num)

        if count_list == []:
            break

    else:
        return None

    out = compile_list[0]
    for i in compile_list[1:]:
        out = out * i

    return out


if __name__ == "__main__":
    from testing_utils import _test_func

    # test_get_value = [  # [Input, Output]
    #     # postive control (works)
    #     ["42.3 gcm-3", (42.3, '42.3')],
    #     ["42.3gcm-3", (42.3, '42.3')],
    #     ["66.11*10**-62 g", (6.611e-61, '66.11*10**-62')],
    #     ["66.11*10**62 cm-3/mol", (6.611e+63, '66.11*10**62')],
    #     ["0.909 g/cm3", (0.909, '0.909')],
    #     ["-0.909 g/cm3", (-0.909, '-0.909')],
    #     ["  -0.909 g/cm3", (-0.909, '-0.909')],
    #     ["0.343", (0.343, '0.343')],
    #
    #     # negative control (fails)
    #     ["c40 °F", (None, None)],
    #     ["", (None, None)],
    #     ["*", (None, None)],
    #     ["*34gd", (None, None)],
    # ]
    # _test_func(_get_value, test_get_value)

    #
    # test_split_list = [
    #     # postive control (changes)
    #     [["fish","pig", "cow"], ["f", "is", "h", "pig", "cow"], {"chunks": ["is"]}],
    #     [["fish", Unit("g"), "cow"], ["f", "is", "h", Unit("g"), "cow"], {"chunks": ["is"]}],
    #     [["fishpigcow"], ["f", "i", "shpigcow"], {"chunks": ["i"]}],
    #     [["fishpigcow"], ["f", "i", "shpig", "c", "ow"], {"chunks": ["i", "c"]}],
    #
    #     # negative control (no changes)
    #     [["fish"], ["fish"], {"chunks": ["fish"]}],
    #     [["fishpigcow"], ["fishpigcow"], {"chunks": ["z"]}],
    #     [[Unit("g")], [Unit("g")], {"chunks": ["is"]}],
    # ]
    # _test_func(_split_list, test_split_list)
    #
    #
    # test_units_in_parenthesis = [
    #     # postive control (changes)
    #     ["° F (yyy, 1992)", ["° F "]],
    #     [["g/(mol * s)"], ["g/", Unit("mol * s")]],
    #     [" g/(mol * s) approx.", [" g/", Unit("mol * s"), " approx."]],
    #
    #     # negative control (no changes)
    #     ["° F NTP, 1992", ["° F NTP, 1992"]],
    #     [["° F NTP, 1992"], ["° F NTP, 1992"]],
    #     [[""], [""]],
    #     [[None], [None]],
    #     [None, None],
    #
    # ]
    # _test_func(_split_on_parenthesis, test_units_in_parenthesis)
    #
    #
    # test_units_with_powers = [
    #     # postive control (changes)
    #     ["g**2cm**-3", [Unit("g**2"), Unit("cm**-3")]],
    #     ["g**2 cm**-3", [Unit("g**2"), " ", Unit("cm**-3")]],
    #     ["g*cm**-3", ["g*", Unit("cm**-3")]],
    #     ["g*cm**-35", ["g*", Unit("cm**-35")]],
    #     ["g cm**-35", ["g ", Unit("cm**-35")]],
    #     ["gcm**-3", ["g*", Unit("cm**-35")]],
    #     ['cm**3/mol', [Unit('cm**3'), '/mol']],
    #
    #     # negative control (no changes)
    #     [["g/(mol * s)"], ["g/(mol * s)"]],
    #     ["° F NTP, 1992", ["° F NTP, 1992"]],
    #     [["° F NTP, 1992"], ["° F NTP, 1992"]],
    #     [[""], [""]],
    #     [[None], [None]],
    #     [None, None],
    #
    # ]
    # _test_func(_split_on_powers, test_units_with_powers)

    # test_merge_split_text = [
    #     # postive control (changes)
    #     [[Unit("g**2"), Unit("cm**-3")], Unit("g**2 * cm**-3")],
    #     [[Unit("g**2"), "*", Unit("cm**-3")], Unit("g**2 * cm**-3")],
    #     [[Unit("g**2"), "/", Unit("cm")], Unit("g**2/cm")],
    #     [["g/(mol * s)"], ["g/(mol * s)"]],
    #
    #     # negative control (no changes)
    #     [["g/(mol * s)"], ["g/(mol * s)"]],
    #     ["° F NTP, 1992", ["° F NTP, 1992"]],
    #     [["° F NTP, 1992"], ["° F NTP, 1992"]],
    #     [[""], [""]],
    #     [[None], [None]],
    #     [None, None],
    #
    # ]
    # _test_func(_merge_split_text, test_merge_split_text)


    # test_frame_shift = [  # [Input, Output]
    #     # postive control (works)
    #     ["gcm", Unit("g*cm")],
    #     ["gcm**3", Unit("g*cm**3")],
    #     [" g", Unit("g")],
    #     ["mlgcm", Unit("ml*g*cm")],
    #
    #     # negative control (fails)
    #     ["- closed cup", None],
    #     ["c40 °F", None],
    #     ["", None],
    #     ["*", None],
    #     ["*34gd", None],
    # ]
    # _test_func(_frame_shift, test_frame_shift)


    # test_get_unit = [  # [Input, Output]
    #     # postive control (works)
    #     ['°C - closed cup', Unit("degC")],
    #     [' °F', Unit('degF')],
    #     ["g/(mol * s)", Unit("g/(mol * s)")],
    #     [' g/(mol * s) approx.', Unit("g/(mol * s)")],
    #     ['°F (NTP, 1992)', Unit("degF")],
    #     ['', Unit("")],
    #     ["g*cm**-3", Unit("g*cm**-3")],
    #     ['cm**3/mol',  Unit('cm**3/mol')],
    #     ['g/mol', Unit('g/mol')],
    #     ["gcm**-3", Unit("g*cm**-3")],
    #     ["g cm**-3", Unit("g*cm**-3")],
    #     ['ml beer.', Unit("ml")],
    #
    #     # negative control (fails)
    #     ["c40 °F", None],
    #     ["*", None],
    #     ["*34gd", None],
    #     [None, None]
    # ]
    # _test_func(_get_unit, test_get_unit)


    test_to_quantity = [  # [Input, Output]
        # # postive control (works)
        ['40 °F ', Quantity("40 degF")],
        ['40°F', Quantity('40 degF')],
        ["42.3 g*cm**-3", Quantity("42.3 g*cm**-3")],
        ['4.0 °C', Quantity("4 degC")],
        [' 4.0 °C', Quantity("4 degC")],
        ['4.0', Quantity("4")],
        ['−66.11*10**-62 cm**3/mol',  Quantity('−66.11*10**-62 cm**3/mol')],
        ['−66.11*10**+62 cm**3/mol',  Quantity('−66.11*10**62 cm**3/mol')],
        ['10e1 g/mol', Quantity('10e1 g/mol')],
        ['4.0 °C (39.2g/(mol*s)approx.) - closed cup', Quantity("4* degC")],
        ['300 ml beer.', Quantity("300 ml")],
        #
        # # negative control (fails)
        ["42.3 gcm-3", None],
        ["c40 °F", None],
        ["", None],
        ["*", None],
        ["*34gd", None],
        ['20.8 mm Hg @ 25 °C', None],
        ['Index of refraction: 1.50920 @ 20 °C/D', None],
        ['Sound travels at 0.34 km/s', None],

    ]
    _test_func(_to_quantity, test_to_quantity)