from functools import wraps


def freeze_class(cls):
    """
    This class decorator prevents the addition of new attribute to the class after __init__.
    """
    cls.__frozen = False

    def frozensetattr(self, key, value):
        if self.__frozen and not hasattr(self, key):
            raise self._error("Class '{}' is frozen. Cannot set '{} = {}'"
                  .format(cls.__name__, key, value))
        else:
            object.__setattr__(self, key, value)

    def init_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.__frozen = True
        return wrapper

    cls.__setattr__ = frozensetattr
    cls.__init__ = init_decorator(cls.__init__)

    return cls


def convert_to_list(func):
    """
    This function decorator allows user to enter a single attribute and it will automatically convert it to a list.
    """
    @wraps(func)
    def _convert_to_list(*args):
        # skip first arg (it is self)
        if not isinstance(args[1], (list, tuple)):
            args = list(args)
            args[1] = [args[1]]
        return func(*args)
    return _convert_to_list
