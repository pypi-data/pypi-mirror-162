import re
import numpy as np


def minify_longlat(input_string: str) -> float:
    """
    Minify longitude and latitude from a string.
    :param input_string: 经纬度字符串,度分秒分隔或其它任意分隔符都可以
    :type input_string: str
    :return: minified-longlat
    :rtype: float
    """
    rule = re.compile(r'[0-9]+\.*[0-9]*')
    rs = rule.findall(input_string)
    rf = np.float32(rs)
    factor = np.array([1, 60, 3600])
    target = factor[:len(rf)]
    rs = (rf / target).sum()
    if (input_string.startswith('-') or
            'w' in input_string.lower() or
            's' in input_string.lower()):
        rs = rs * -1
    return rs
