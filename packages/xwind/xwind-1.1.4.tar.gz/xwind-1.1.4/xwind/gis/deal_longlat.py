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


def format_long_lat(long_lat: float) -> str:
    """
    Format longitude and latitude to a string.
    :param long_lat: longitude and latitude
    :type long_lat: float
    :return: formatted-longlat
    :rtype: str
    """
    if long_lat < 0:
        long_lat = long_lat * -1
        sign = '-'
    else:
        sign = ''
    d = int(long_lat)
    m = int((long_lat - d) * 60)
    s = (long_lat - d - m / 60) * 3600
    return sign + str(d) + '°' + str(m) + '′' + f'{s:.2f}' + '″'
