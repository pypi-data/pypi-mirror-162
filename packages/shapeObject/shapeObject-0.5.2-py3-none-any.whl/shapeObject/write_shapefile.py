from shapely.geometry import mapping, Polygon, MultiPolygon, LineString, Point
import shapefile as shp


def set_polygon_geometry(geometry):
    """
    Write MultiPolygons was required

    :param geometry: A Polygon or MultiPolygon
    :return: The coordinates to write into the pyshp's shapefile
    """
    mapped = mapping(geometry)

    if mapped["type"] == "Polygon":
        return [part for part in mapped["coordinates"]]
    elif mapped["type"] == "MultiPolygon":
        return [part for polygon in mapped["coordinates"] for part in polygon]
    else:
        raise TypeError(f"set_poly_geometry is used to write Polygons and MultiPolygons yet found {mapped['type']}")


def write_shape_file(write_directory, file_name, headers, write_geometry, write_records, write_type="Polygon"):
    """
    This takes a set of shapely geometry and writes it to a shapefile at a given directory with the name file_name
    """

    shape_file = shp.Writer(f"{write_directory}/{file_name}")

    # Set the write type
    if (write_type == "Polygon") or (write_type == 5):
        shape_file.shapeType = 5
    elif (write_type == "Line") or (write_type == 3):
        shape_file.shapeType = 3
    elif (write_type == "Point") or (write_type == 1):
        shape_file.shapeType = 1
    else:
        raise ValueError(f"write_types takes 'Polygon' (5), 'Line' (3), or 'Point' (1)\n")

    # Set the fields
    # TODO We need to allow for field types but this is leading to byte errors.
    [shape_file.field(field) for field in headers]

    for geo, rec in zip(write_geometry, write_records):
        # Need the asterisk to determine that it is a list rather than a dict or a string set of inputs
        shape_file.record(*rec)

        if isinstance(geo, (Polygon, MultiPolygon)):
            shape_file.poly(set_polygon_geometry(geo))

        elif isinstance(geo, LineString):
            shape_file.line([[list(line) for line in mapping(geo)["coordinates"]]])

        elif isinstance(geo, Point):
            shape_file.point(geo.x, geo.y)

        else:
            raise TypeError(f"Expected to write Polygons, Multipolygons, Lines, or Points yet found {type(geo)}\n")
