import time
from typing import List


def now_timestamps() -> int:
    return int(time.time())


def dict_deep_get(dictionary, paths, default=None):
    """
    深度获取字典值
    """
    if not isinstance(paths, List):
        paths = paths.split(".")
    for key in paths:
        try:
            dictionary = dictionary[key]
        except KeyError:
            return default
    return dictionary
