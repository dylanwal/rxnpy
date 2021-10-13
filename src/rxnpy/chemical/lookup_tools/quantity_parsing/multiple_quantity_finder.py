from typing import List, Optional, Any
import re

from testing_utils import _test_func


def multiple_quantites_main(text_in):
    text_list = _multiple_quantites(text_in)
    out = []
    for text in text_list:
        out.append(_condition_finder(text))

    return out

def _multiple_quantites(text_in: str) -> List[str]:
    result = re.split(";", text_in)
    return [text.strip() for text in result]


def _condition_finder(text_in: str):
    """
    Extracts conditions and creates list [quantity, conditions]

    Warning: replace 'at' with '@' first (use _substitutions_general in pre_processing.py)
    """
    if "@" in text_in:
        result = re.split("@", text_in)
        return [text.strip() for text in result]
    elif "(" in text_in:
        in_parenthesis = re.findall("[(].*[0-9]{1}.*[)]", text_in)
        if len(in_parenthesis) == 1:
            text_in = text_in.replace(in_parenthesis[0], "")
            result = [text_in, in_parenthesis[0][1:-1]]
        return [text.strip() for text in result]

    return [text_in]


if __name__ == "__main__":
    from testing_utils import _test_func
    test_multiple_quantites = [  # [Input, Output]
        # postive control (works)
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
    _test_func(_multiple_quantites, test_multiple_quantites)


    test_condition_finder = [  # [Input, Output]
        # postive control (works)
        ['18 mm Hg @ 68 °F ', ['18 mm Hg', '68 °F']],
        ['20 mm Hg @ 77° F', ['20 mm Hg', '77° F']],
        [' 20 mm Hg @ 77° F (NTP, 1992)', ['20 mm Hg', '77° F (NTP, 1992)']],

        # negative control (fails)
        ['20.8 mm Hg 25 °C', ['20.8 mm Hg 25 °C']],
        ['20.8 mm Hgat25 °C', ['20.8 mm Hgat25 °C']],
        ['Pass me a 300 ml beer.', ['Pass me a 300 ml beer.']],
        ["42.3 gcm-3", ["42.3 gcm-3"]],
        ["40 °F", ["40 °F"]],
        ["39.2 g/[mol * s]]", ["39.2 g/[mol * s]]"]],
        ['−66.11·10-62 cm3/mol', ['−66.11·10-62 cm3/mol']]
    ]
    _test_func(_condition_finder, test_condition_finder)