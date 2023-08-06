from .ShapeObject import ShapeObject
from .write_shapefile import write_shape_file
from .supports import multi_to_poly
from shapely.geometry import Polygon, MultiPolygon

from typing import Union, List, Tuple
from pathlib import Path


class MergeCommonShapes:
    """
    If a shapefile is made up of multiple polygons representing the same place, then this method will join them into
    a multipolygon based on a common ID.
    """
    def __init__(self, shp_path: Union[str, Path], id_index: int, header_indexes: List[int]):

        self.shp_obj = ShapeObject(shp_path)
        self.gid = id_index
        self.header_indexes = header_indexes

    def __call__(self, write_dir: Union[str, Path], write_name: str, write_headers: List[str]) -> None:
        """Construct the reformatted shapefile with merged common geometry"""
        reformatted = [self._format_shape(gid) for gid in self._unique_gid()]
        write_shape_file(
            write_dir, write_name, write_headers, [shp for shp, rec in reformatted], [rec for shp, rec in reformatted])

    def _unique_gid(self) -> List:
        """Isolate the unique identifiers"""
        return sorted(list(set([r[self.gid] for r in self.shp_obj.records])))

    def _format_shape(self, gid: Union[int, str]) -> Tuple[Union[Polygon, MultiPolygon], List[str]]:
        """
        If more than a single shape of the same ID exists, merge the shapes into a MultiPolygon. Regardless of length,
        isolate and format the attribute data in the order of header_index
        """
        matched = self._isolate_matching(gid)
        if len(matched) > 1:
            return self._isolate_polygons(matched), self._set_headers(matched[0][1])
        else:
            return matched[0][0], self._set_headers(matched[0][1])

    @staticmethod
    def _isolate_polygons(matched):
        """
        If multiple Polygons exist, merge them into a MultiPolygon. If the nested polygons are themselves multipolygons,
        then split those polygons first
        """
        return MultiPolygon([shp for polys in [multi_to_poly(shp) for shp, _ in matched] for shp in polys])

    def _isolate_matching(self, gid: Union[str, int]):
        """Isolate all the shapes that match the current unique GID"""
        return [[shp, rec] for shp, rec in zip(self.shp_obj.polygons, self.shp_obj.records) if rec[self.gid] == gid]

    def _set_headers(self, headers: List[str]) -> List[str]:
        """Isolate each column i in the order of header_indexes"""
        return [headers[i] for i in self.header_indexes]

