import pandas as pd
from pyproj import Transformer

from .objects.geo_point import GeoPoint


def transform(epsg_origin: int, epsg_target: int, coordinates: GeoPoint) -> GeoPoint:
    """变换坐标

    Args:
        epsg_origin (int): crs_from，指示坐标当前坐标系统的epsg代码
        epsg_target (int): crs_to,指示坐标想要转换的目标坐标系统的epsg代码
        coordinates (Geo_Point): 地理坐标系统

    Returns:
        Geo_Point: 地理系统坐标
    """
    trans = Transformer.from_crs(epsg_origin, epsg_target)
    x, y = trans.transform(coordinates.latitude, coordinates.longitude)
    return GeoPoint(x, y)


def transform_table(epsg_origin: int, epsg_target: int, table: pd.DataFrame) -> pd.DataFrame:
    trans = Transformer.from_crs(epsg_origin, epsg_target)
    for i,row in table.iterrows():
        lat,long = row['lat'],row['long']
        nlat,nlong = trans.transform()
    table['transform'] = table.apply(lambda row: transform(epsg_origin, epsg_target, GeoPoint(row['lat'], row['long'])),
                                     axis=1)
    for index, r in table.iterrows():
        x, y = r['lat'], r['long']
        p = transform(epsg_origin, epsg_target, GeoPoint(x, y))
        r['lat'] = p.latitude
        r['long'] = p.longitude

    return table
