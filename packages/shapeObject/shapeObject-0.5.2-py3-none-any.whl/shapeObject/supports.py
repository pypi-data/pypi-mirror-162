from shapely.geometry import Polygon, MultiPolygon
from typing import Union, List


def multi_to_poly(polygon_to_be_typed: Union[Polygon, MultiPolygon]) -> List[Polygon]:
    """
    Recasts all geometry to be Shapely Polygons

    Some methods, like shapely split, do not work well on MultiPolygons and can lead to errors. This method recasts all
    polygons to be a list of polygons.
    """
    if polygon_to_be_typed.geom_type == "MultiPolygon":
        return [poly for poly in polygon_to_be_typed]
    else:
        return [polygon_to_be_typed]