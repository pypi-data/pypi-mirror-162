import json
import sys
from collections.abc import Mapping
from typing import Any, List, Union


def _is_basic_type(item: Any):
    if isinstance(item, (int, str, float, bool)):
        return True
    return False


class MJson(Mapping):
    def __init__(self, value: dict):
        self._value = value

    def __getitem__(self, key: Union[str, int, List[Union[int, str]]]):
        if isinstance(key, str):
            t_value = self._value[key]
        else:
            t_value = self._value
            for k in key:
                t_value = t_value[k]
        if _is_basic_type(t_value):
            return t_value
        else:
            return MJson(t_value)

    def __iter__(self):
        for item in self._value:
            if _is_basic_type(item):
                yield item
            else:
                yield MJson(item)

    def __len__(self):
        return len(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def value(self):
        return self._value

    @classmethod
    def loads(cls, s, **kw) -> "MJson":
        value = json.loads(s, **kw)
        return MJson(value)

    def get(self, key: Union[str, int, List[Union[int, str]]], default: Any = None):
        try:
            return self.__getitem__(key)
        except (KeyError, IndexError):
            return default

    def get_value(self, key: Union[str, int, List[Union[int, str]]], default: Any = None):
        try:
            res = self.__getitem__(key)
            if isinstance(res, MJson):
                return res._value
            else:
                return res
        except (KeyError, IndexError):
            return default

    def find_by_key(self, key: str, count: int = -1):
        if count <= 0:
            count = sys.maxsize
        res = []
        temp_nodes = [self]
        while temp_nodes:
            node = temp_nodes.pop(0)
            if isinstance(node.value, dict):
                for k, v in node.items():
                    if k == key:
                        res.append(v)
                        if len(res) == count:
                            return res
                    if not _is_basic_type(v):
                        temp_nodes.append(v)
            elif isinstance(node.value, list):
                for v in node:
                    if not _is_basic_type(v):
                        temp_nodes.append(v)
        return res

    def find_one_by_key(self, key: str):
        res = self.find_by_key(key, 1)
        if res:
            return res[0]
        return None
