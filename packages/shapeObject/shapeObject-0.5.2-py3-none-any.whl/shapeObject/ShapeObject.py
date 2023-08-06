from shapely.geometry import Polygon, MultiPolygon, Point, LineString
from distutils.util import strtobool
from typing import Union
from pathlib import Path
import shapefile as shp


class ShapeObject:
    """
    Create an objected from a shapefile with shapely compatible geometry
    """

    def __init__(self, load_path: Union[Path, str], encoding: str = 'utf-8', encoding_errors: str = 'strict'):
        """
        Creates an object from loading in a shapefile via pyshp. This class then converts the geometry to be shapely
        compatible and loads other data like records/parameters into there own class object holders.

        Takes a path to a file, an optional parameters to set the coding and how to handle errors


        """
        self.file_name = Path(load_path).name

        # Use pyshp to create a Reader for the shapefile, and use it to extract the raw records
        self._shapefile = shp.Reader(load_path, encoding=encoding, encodingErrors=encoding_errors)
        self._records = self._extract_records()

        # Set the fields of the shapefile
        self.field_names = self._extract_field(0)
        self.field_types = self._set_field_types()

        # Extract the raw geometry to be accessed via respective properties
        self._geometry = self._extract_geometry()

        # Set the type for the user to look at and for internal usage
        self._type_dict = {1: "points", 3: "edges", 5: "polygons", 15: 'polygons'}
        self.shapefile_type = self._type_dict[self._shapefile.shapeType]

    def __repr__(self):
        """The current file contains (Number of elements) of type self.shapefile_type"""
        return f"{self.file_name} contains {len(getattr(self, self.shapefile_type))} {self.shapefile_type}"

    def _extract_field(self, index: int):
        """
        Takes a index to parse out information from the list of record column information

        Further Information
        --------------------
        pyshp will only read records values that are 0x20 otherwise it will be set ot a DeletionFlag. Commonly, the
        index of the records is set to a value type that will lead to a DeletionFlag rather than a record column that
        can be loaded, but if the user has a shapefile that has none 0x20 values they will be purged here.

        pyshp fields have 4 values for each field, the filed name, the field type, field length and decimal length.

        :param index: The index to call a column pyshp value. 0-name, 1-type, 2-length, 3-decimal length
        :type index: int

        :return: List of indexed pyshp field information
        :rtype: list
        """
        return [field[index] for field in self._shapefile.fields if field[0] != "DeletionFlag"]

    def _set_field_types(self):
        """
        Convert Pyshp field types to python types

        Further Information
        ---------------------
        Pyshp sets field types to be 'C' for characters, "N" for numbers without decimal places, "F" for floats, "L" for
        bools, "D" for dates amd "M" for memo. These are concert into str, int, float, bool, str, str respectively.
        Pyshp does this conversion on records automatically, but if needed this represents a way to convert a row of a
        record to the type of that record

        :return: A list of python types, where each element is the python type representation of the shapefile field
            type
        """
        type_list = {"C": str, "N": int, "F": float, "L": self._string_to_bool, "D": str, "M": str}
        return [type_list[field_type] for field_type in self._extract_field(1)]

    @staticmethod
    def _string_to_bool(string_representation_of_bool: str):
        """
        Convert a string of False or True to a bool representation
        """
        return bool(strtobool(string_representation_of_bool))

    def _extract_records(self):
        """
        Extract the records from the pyshp record list

        :return: A list of records, where each element in the list represents one row in the attribute table
        :rtype: list
        """
        return [record for record in self._shapefile.records()]

    def _extract_geometry_data(self, index: int):
        """
        Returns the type of the current geometry for the current indexed piece of geometry in the shapefile

        :param index: The current index item to load from the list of geometry
        :type index: int

        :return: A tuple of a string and a list, with the string being the type the geometry is and the list the
            coordinates
        :rtype: tuple[str, list]
        """
        if self._shapefile.shape(index).shapeTypeName != "NULL":
            json_info = self._shapefile.shape(index).__geo_interface__
            return json_info["type"], json_info["coordinates"]
        else:
            return "Null", []

    def _extract_geometry(self):
        """
        Returns lists of homogeneous shapely types and the records for these given types

        Further Information
        --------------------
        Geometry can be grouped into three core collection types: Points, Lines and Polygons. Some of these types have
        multiple sub types, for example a polygon may be a single polygon or a multipolygon. This extracts the geometry
        and returns a dict containing each homogeneous type. In the case of multiple types in a given shapefile, if
        records where not indexed by type, then the length of records would not match the type leading to problems.

        Warning
        -----
        Currently does not have support for multi-linestrings, or linear rings.

        :return: A list of each homogeneous geometry type
        """
        geometry = {"Polygon": {"Geometry": [], "Records": []},
                    "Edge": {"Geometry": [], "Records": []},
                    "Point": {"Geometry": [], "Records": []}}

        for i, record in enumerate(self._records):
            geometry_type, geometry_point_set = self._extract_geometry_data(i)

            if geometry_type == "Polygon":
                geometry["Polygon"]["Geometry"].append(self._set_shapely_polygon(geometry_point_set, i))
                geometry["Polygon"]["Records"].append(record)

            elif geometry_type == "MultiPolygon":
                geometry["Polygon"]["Geometry"].append(MultiPolygon([self._set_shapely_polygon(poly_point_set, i)
                                                                     for poly_point_set in geometry_point_set]))
                geometry["Polygon"]["Records"].append(record)

            elif geometry_type == "Point":
                geometry["Point"]["Geometry"].append(Point(geometry_point_set))
                geometry["Point"]["Records"].append(record)

            elif geometry_type == "LineString":
                geometry["Edge"]["Geometry"].append(LineString(geometry_point_set))
                geometry["Edge"]["Records"].append(record)

            elif geometry_type == "Null":
                print(f"Null found for {i}th element, which was skipped")

            else:
                print(f"Sorry: {geometry_type} not currently supported")

        return geometry

    def _set_shapely_polygon(self, polygon_point_set, index):
        """
        Return a valid shapely polygon

        Further information
        --------------------
        If a polygon_point_set's length is only equal to one, then it will just be a simple polygon without any holes
        within it, otherwise there are holes in the polygon. The way that Esri encodes the polygons is that the first
        coordinate set of points is the shape with holes in it, and all other sets of points are the holes which are
        encoded in a counter clockwise manner so that the system knows it is a hole when drawing it. Shapely works the
        exact same way, the first instance is the polygons hull with the second optional argument being a list counter
        clockwise points sets that represent the holes

        A polygon may not be valid, which may lead to problems using shapely functions later on. If an invalid polygon
        is found it is buffered at width zero. This should return the closest possible shape to what the polygon was
        with the benefit of being valid

        :param polygon_point_set: A grouped list of coordinates for a given polygon, where the first element is the hull
            of the polygon and all later elements a counter clockwise ring of points that indicate any holes in the
            polygon
        :type polygon_point_set: list

        :param index: The current index item to load from the list of geometry
        :type index: int

        :return: A shapely Polygon
        :rtype: shapely.geometry.polygon.Polygon
        """

        if len(polygon_point_set) > 1:
            # Polygon with holes
            polygon = Polygon(polygon_point_set[0], [hole for hole in polygon_point_set[1:]])
        else:
            # Single polygon
            polygon = Polygon(polygon_point_set[0])

        if polygon.is_valid:
            return polygon
        else:
            print(f"Invalid Polygon found for {self._records[index]}: Buffering")
            return polygon.buffer(0)

    @property
    def polygons(self):
        """
        Points from the extracted geometry if correct type, else TypeError

        :return: [Polygons1 ... PolygonN] Polygons
        :rtype: list[Polygon]
        """
        if self.shapefile_type == "polygons":
            return [poly for poly in self._geometry["Polygon"]["Geometry"]]
        else:
            return TypeError(f"Polygons called but shapefile type is {self.shapefile_type}")

    @property
    def edges(self):
        """
        Edges from the extracted geometry if correct type, else TypeError

        :return: [Edge1 ... EdgeN] Edges
        :rtype: list[LineString]
        """
        if self.shapefile_type == "edges":
            return [edge for edge in self._geometry["Edge"]["Geometry"]]
        else:
            raise TypeError(f"Edges called but shapefile type is {self.shapefile_type}")

    @property
    def points(self):
        """
        Points from the extracted geometry if correct type, else TypeError

        :return: [Point1 ... PointN] Points
        :rtype: list[Point]

        """
        if self.shapefile_type == "points":
            return [point for point in self._geometry["Point"]["Geometry"]]
        else:
            raise TypeError(f"Points called but shapefile type is {self.shapefile_type}")

    @property
    def records(self):
        """Return the relevant records to the shape type"""
        if self.shapefile_type == "polygons":
            return [rec for rec in self._geometry["Polygon"]["Records"]]
        elif self.shapefile_type == "edges":
            return [rec for rec in self._geometry["Edge"]["Records"]]
        elif self.shapefile_type == "points":
            return [rec for rec in self._geometry["Point"]["Records"]]
        else:
            raise ValueError(f"Expected values of shapeType are 1, 3, and 5 yet found {self.shapefile_type}")
