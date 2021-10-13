
def sig_figs(number: float, significant_digit: int = 3) -> float:
    """
    Given a number return a string rounded to the desired significant digits.
    :param number:
    :param significant_figures:
    :return:
    """
    return float('{:.{p}g}'.format(number, p=significant_digit))


if __name__ == "__main__":
    from testing_utils import _test_func

    test_round_off = [  # [Input, Output]
        # postive control (works)
        [234.2342300000001, 234.23423, {"significant_digit": 15}],
        [234.2342399999999999, 234.23424, {"significant_digit": 15}],
        [234.2342300000001, 234.23, {"significant_digit": 5}],
        [234.2342399999999999, 234.23, {"significant_digit": 5}],
        [234.2342399999999999, 200, {"significant_digit": 1}],
        [-234.2342399999999999, -200, {"significant_digit": 1}],
        [-234.2342399999999999, -234.23424, {"significant_digit": 15}],
        # negative control (fails)

    ]
    print("\nTest 'remove_round_off_error'")
    _test_func(sig_figs, test_round_off)