from typing import List, Any


def _test_func(func, tests_stuff, kwarg = None):
    print(f"Testing: '{func.__name__}'")
    num_tests = len(tests_stuff)
    ok_tests = 0
    for t in tests_stuff:
        input_ = t[0]
        output_ = t[1]
        kwargs = {}
        if kwarg is not None:
            kwargs = kwarg
        if len(t) == 3:
            kwargs = t[2]
        try:
            assert output_ == (value := func(input_, **kwargs))
        except AssertionError:
            print(f"ERROR:'{input_}' -> '{value}' (Expected: '{output_}')")
            continue
        print(f"OK: '{input_}' -> '{output_}'")
        ok_tests += 1

    print(f"{ok_tests}/{num_tests} passed!")
    print("")
