import abc
from enum import Enum

from pint import Quantity


class Serializable(abc.ABC):

    def as_dict(self, remove_none: bool = False, skip: list[str] = None) -> dict:
        """Convert and return object as dictionary."""
        skip = [] if skip is None else skip
        keys = {k.lstrip("_") for k in vars(self) if ("__" not in k) and (k not in skip)}

        attr = dict()
        for k in keys:
            value = self.__getattribute__(k)
            if remove_none and (value is None or value == "" or value == [] or value == {}):
                continue
            elif isinstance(value, Quantity) or isinstance(value, Enum):
                value = str(value)
            else:
                value = self._to_dict(value)
            attr[k] = value

        return attr

    def _to_dict(self, obj):
        """Convert obj to a dictionary, and return it."""
        if isinstance(obj, list):
            return [self._to_dict(i) for i in obj]
        elif hasattr(obj, "as_dict"):
            return obj.as_dict()
        else:
            return obj

