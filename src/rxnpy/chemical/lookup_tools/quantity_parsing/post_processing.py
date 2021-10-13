from typing import List, Optional, Any, Union, Tuple

from src.rxnpy import Unit, Quantity


def _remove_duplicates(list_quantities: List[Quantity]) -> List[Quantity]:
    return list_quantities


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
