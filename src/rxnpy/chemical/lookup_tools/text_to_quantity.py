import re
from statistics import mean
from typing import List, Optional, Union, Any
from functools import wraps

from pint.errors import OffsetUnitCalculusError, UndefinedUnitError, DefinitionSyntaxError

from src.rxnpy import Unit, Quantity


PATTERN_PREPROCESSING = [  # [serach pattern, replace]
    ["[\(].*[\)]", ""],  # remove stuff in parenthesis
    ["^[a-zA-Z;,.: /]*", ""], # remove text at front of strings
    ["@", "at", ""], # replace @ with at
    ["={1}.*$", ""], # if equals in string take first term
]


PATTERN_LIST_IN_STRING = [

]


PATTERN_CONDITIONS = [
    "[-.0-9]{1,7} {0,1}[^0-9,/;]{0,8} at [-.0-9]{1,7} {0,1}[^0-9,/;]{0,8}"
]


PATTERN_RANGE = [
    "([-.0-9]{1,6}[- ]{1,3}[-.0-9]{1,6})",
    "([-.0-9]{1,6}[^0-9-,/;]{0,8}[- ]{1,3}[-.0-9]{1,6}[^0-9,/;]{0,8})"
]


def debug_print(func):
    """Prints out text passing through it."""
    @wraps(func)
    def _debug_print(*args, **kwargs):
        if args[0].debug:
            print(func.__name__ + ": " + args[1])
        return func(*args, **kwargs)
    return _debug_print


class TextToQuanity:

    def __init__(self,
        text_in: Optional[str] = None,
        patterns_pre_processing: Optional[Union[List[str], str]] = PATTERN_PREPROCESSING,
        patterns_list_in_string: Optional[List[str]] = PATTERN_LIST_IN_STRING,
        patterns_conditions: Optional[List[str]] = PATTERN_CONDITIONS,
        patterns_range: Optional[List[str]] = PATTERN_RANGE,
        debug: Optional[bool] = False
        ):
        """
        Given a text string; create quanity.
        :param text_in: text to be processed
        :param pre_processing_patterns:
        :param patterns_list_in_string:
        :param patterns_conditions:
        :param patterns_range:
        :param debug: get print out
        """
        self.patterns_pre_processing = patterns_pre_processing
        self.patterns_list_in_string = patterns_list_in_string
        self.patterns_conditions = patterns_conditions
        self.patterns_range = patterns_range
        self.debug = debug

        self.text_in = text_in
        self.out = None

    def __call__(self, text_in: Union[str, List[str]], **kwargs)-> Quantity:
        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise ValueError(f"Invalid attribute passed: {k}: {v}")

        self.text_in = text_in
        if isinstance(text_in, list):
            return self._list(text_in)
        elif isinstance(text_in, str):
            return self._text(text_in)

    def _text(self, text_in: str) -> Any:
        """Main entry point for simple text processing."""
        if not self.contains_number(text_in):
            return None

        text_in = self._pre_processing(text_in)

        flag, result = self._check_for_list_in_string(text_in)
        if flag: return result
        flag, result = self._check_for_conditions(text_in)
        if flag: return result

        text_in = self._check_for_range(text_in)

        return self._to_quantity(text_in)

    def _list(self, list_in):
        """Main entry point for simple text processing."""
        pass

    @staticmethod
    def contains_number(obj_in: Union[str, List]) -> bool:
        """ Checks list to see if it has a number in it anywhere."""
        _pattern = r'\d'
        if isinstance(obj_in, list):
            return any([bool(re.search(_pattern, value)) for value in obj_in])
        elif isinstance(obj_in, str):
            return bool(re.search(_pattern, obj_in))
        else:
            raise TypeError

    @debug_print
    def _pre_processing(self, text_in) -> str:
        """General pre_processing to remove unuseful stuff."""
        for pattern in self.patterns_pre_processing:
            text_in = re.sub(pattern[0], pattern[1], text_in)

        return text_in

    @debug_print
    def _check_for_list_in_string(self, text_in) -> (bool, Any):
        """ """
        for pattern in self.patterns_list_in_string:
            text_out = re.findall(pattern, text_in)
            if text_out is not None:
                return True, self.list_text_to_quanity(text_out)

        return False, text_in

    @debug_print
    def _check_for_conditions(self, text_in) -> (bool, Any):
        """If values come with coditions """
        for pattern in self.patterns_conditions:
            text_out = re.findall(pattern, text_in)
            if len(text_out) == 2:
                main_value = self._to_quantity(text_out[0])
                cond = self._to_quantity(text_out[1])
                return True, [main_value, cond]

        return False, text_in

    @debug_print
    def _check_for_range(self, text_in) -> str:
        """ """
        for pattern in self.patterns_range:
            text_out = re.findall(pattern, text_in)
            if not (text_out == []) and len(text_out) == 1:
                return text_out[0]

        return text_in

    @debug_print
    def _to_quantity(self, text: str) -> Quantity:
        value = re.findall('^[0-9.-]+', text.lstrip())[0]
        unit = text.strip(value).replace(" ", "")

        unit = re.sub("LB", "lb", unit)
        find_dash = re.search("[^0-9]{1}-{1}[^0-9]{1}", unit)
        if find_dash is not None:
            unit = unit[:find_dash.span()[0 ] +1] + "*" + unit[find_dash.span()[1 ] -1:]

        try:
            try:
                return float(value) * Unit(unit)
            except OffsetUnitCalculusError:
                if re.findall('F', text):
                    return float(value) * Unit("degF")
                elif re.findall("C", text):
                    return float(value) * Unit("degC")
        except UndefinedUnitError:
            pass

        return None

    @debug_print
    def _reduce_unit_list(self, list) -> Quantity:
        """ """
        if len(data_in) <= 2:
            return data_in[0]

        # find most common dimnsion and filter out any bad ones.
        unit_dimnsionality_count = {}
        for data in data_in:
            if data.dimensionality not in unit_dimnsionality_count:
                unit_dimnsionality_count[data.dimensionality] = 1
            else:
                unit_dimnsionality_count[data.dimensionality] += 1

        most_common_unit = max(unit_dimnsionality_count, key=unit_dimnsionality_count.get)
        data_in = [data for data in data_in if most_common_unit == data.dimensionality]

        # remove data furthest from average till 1 point left
        for i in range(len(data_in ) -1):
            data_average = sum([data.to_base_units() for data in data_in] ) /len(data_in)
            differance_list = [abs(data.to_base_units( ) -data_average) for data in data_in]
            data_in.pop(differance_list.index(max(differance_list)))

        return data_in[0]


text_to_quanity = TextToQuanity()


if __name__ == "__main__":
    examples = [
        '40 °F (NTP, 1992)',
        '4.0 °C (39.2 °F) - closed cup',
        '4.0 °C [39.2 g/[mol * s]] - closed cup',
        '4.0 °C [39.2 g/[mol * s] approx.] - closed cup',
        '4.0 °C [39.2g/[mol*s] approx.] - closed cup',
        '4.0 °C [39.2g/[mol*s]approx.] - closed cup',
        '42.3 gcm-3',
        '42.3 g cm-3'
        '40°F',
        '40 °F',
        '115.2-115.3 °C',
        '115.2 - 115.3 °C',
        '-40 °F',
        '20.80 mmHg',
        '18 mm Hg at 68 °F ; 20 mm Hg at 77° F (NTP, 1992)',
        'Vapor pressure, kPa at 20 °C: 2.0',
        '20.8 mm Hg @ 25 °C',
        '20.8 mm Hg (25 °C)',
        '20.8 mm Hg at 25 °C',
        '10e1 g/mol',
        '−66.11·10-62 cm3/mol',
        '−66.11·10+62 cm3/mol',
        '-14.390 BTU/LB= -7992 CAL/G= -334.6X10+5 J/KG',
        'Index of refraction: 1.50920 @ 20 °C/D',
    ]


    quantities = []
    for q in examples:
        #result = text_to_quanity(q, debug=True)
        result = _iterative_unit_finder(q)
        print(result)
        quantities.append(result)