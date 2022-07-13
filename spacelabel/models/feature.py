import logging

import numpy

from astropy.time import Time
from numpy import ndarray
from shapely.geometry import LinearRing
from shapely.geometry import Polygon, box
from tfcat import Feature as TFCatFeature
from tfcat import Polygon as TFCatPolygon
from tfcat import MultiLineString as TFCatMultiLineString
from spacelabel.models.crs import CRS

from typing import List, Tuple, Optional

log = logging.getLogger(__name__)


class Feature:
    """
    A named 'feature' from the observational data, which is described by a polygon on the time-frequency plane.
    """
    _name: str = None
    _time: Time = None
    _freq: ndarray = None
    _id: int = None
#    _ax_data: Dict[str, Axes] = None

    def __init__(
            self, name: str,
            vertexes: List[Tuple[Time, float]],
            feature_id: int,
            log_level: Optional[int] = None
    ):
        """
        Initialize the feature.

        :param name: The name of the feature
        :param vertexes: The time-frequency pairs of the vertexes defining it
        :param feature_id: The internal ID number for the feature
        :param log_level: The level of logging to show. Inherited from DataSet
        """
        self._name = name
        self._id = feature_id
        self._time = Time([vertex[0] for vertex in vertexes])
        self._freq = numpy.array([vertex[1] for vertex in vertexes])

        if log_level:
            log.setLevel(log_level)

    @property
    def _coordinates(self):
        coordinates = self.vertexes(unix_time=True)
        # TFcat format is counter-clockwise, so invert if our co-ordinates are not
        if not LinearRing(coordinates).is_ccw:
            coordinates = coordinates[::-1]
        return coordinates

    def crop(self, bbox: Tuple):
        """
        Crops the feature to have the vertexes inside the plotting window
        """

        polygon = Polygon(self._coordinates)
        polygon = polygon.intersection(box(bbox[0].unix, bbox[1], bbox[2].unix, bbox[3]))

        self._time = CRS.time_converter(polygon.exterior.xy[0])
        self._freq = numpy.array(polygon.exterior.xy[1])

    @property
    def to_text_summary(self) -> str:
        """
        Writes a summary of the feature's extent to text.

        :return: A string containing the feature name, and its maximum and minimum bounds in the time-frequency plane
        """
        return f"{self._name}, {min(self._time)}, {max(self._time)}, {min(self._freq)}, {max(self._freq)}"

    def tfcat_feature(self, bbox=None) -> TFCatFeature:
        """TFCat Feature instance of current event.

        :return: A TFCat Feature object. Times are returned as Unix time, not calendar time
        """

        if bbox is not None:
            self.crop(bbox)

        # check if polygon is closed:
        if self._coordinates[0] == self._coordinates[-1]:
            geometry = TFCatPolygon
        else:
            geometry = TFCatMultiLineString

        return TFCatFeature(
            geometry=geometry([self._coordinates]),
            id=self._id,
            properties={
                "feature_type": self._name
            }
        )

    def to_tfcat_dict(self, bbox=None) -> dict:
        """
        Expresses the polygon in the form of a dictionary containing a TFCat feature.

        :return: A TFCat. Times are returned as Unix time, not calendar time
        """

        return self.tfcat_feature(bbox=bbox)

    def is_in_time_range(self, time_start: Time, time_end: Time) -> bool:
        """
        Whether the feature is within this time range.

        :param time_start: The start of the time range (inclusive)
        :param time_end: The end of the time range (inclusive)
        :return: Whether the time range contains any part of this feature
        """
        return (time_start <= self._time.min() <= time_end) or (time_start <= self._time.max() <= time_end)

    def vertexes(self, unix_time=False) -> List[Tuple[Time, float]]:
        """
        Returns the vertexes of the polygon as a list of tuples of time-frequency points.

        :return: List of vertexes as (time, frequency)
        """
        if unix_time:
            time_converter = lambda x: float(x.unix)
        else:
            time_converter = lambda x: x
        return [
            (time_converter(time), freq) for time, freq in zip(self._time, self._freq)
        ]

    def arrays(self) -> Tuple[Time, ndarray]:
        """
        Returns the arrays of the poly co-ordinates

        :return: The co-ordinates in seperated arrays
        """
        return (
            self._time, self._freq
        )
