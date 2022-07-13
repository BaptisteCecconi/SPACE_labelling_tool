# -*- coding: utf-8 -*-
"""Test SPACE Labelling Tool Models/Feature module."""

import pytest
from spacelabel.models.feature import Feature
from tfcat import Feature as TFCatFeature
from astropy.time import Time
from shapely.geometry import LinearRing
import numpy
from astropy.units import Unit


@pytest.fixture
def feature_data_0():
    """Feature id 0 from test data"""
    return {
        "vertexes": [
            (Time(1141259072.0, format="unix"), 717.1033199519603),
            (Time(1141249646.0, format="unix"), 139.3051766316289),
            (Time(1141278883.0, format="unix"), 43.9369897680012),
            (Time(1141291505.0, format="unix"), 133.02148046593334),
            (Time(1141279682.0, format="unix"), 823.6034703431599),
            (Time(1141264025.0, format="unix"), 1021.559655691171)
        ],
        "feature_id": 0,
        "name": "some_feature1"
    }


@pytest.fixture
def feature_data_1():
    """Feature id 1 from test data"""
    return {
        "vertexes": [
            (Time(1141259072.0, format="unix"), 717.1033199519603),
            (Time(1141249646.0, format="unix"), 139.3051766316289),
            (Time(1141278883.0, format="unix"), 43.9369897680012),
            (Time(1141291505.0, format="unix"), 133.02148046593334),
            (Time(1141279682.0, format="unix"), 823.6034703431599),
            (Time(1141264025.0, format="unix"), 1021.559655691171),
            (Time(1141259072.0, format="unix"), 717.1033199519603),
        ],
        "feature_id": 1,
        "name": "some_feature2"
    }


@pytest.fixture
def feature_0(feature_data_0):
    return Feature(**feature_data_0)


@pytest.fixture
def feature_1(feature_data_1):
    return Feature(**feature_data_1)


@pytest.fixture
def data_bbox():
    return []


@pytest.fixture
def coordinates_crop_fmax_510():
    return [
        (1141255693.3877347, 510.0),
        (1141249646.0, 139.3051766316289),
        (1141278883.0, 43.9369897680012),
        (1141291505.0, 133.02148046593334),
        (1141285050.9987347, 510.0),
        (1141255693.3877347, 510.0)
    ]

def test_feature(feature_0):
    assert isinstance(feature_0, Feature)


def test_vertexes(feature_0, feature_data_0):
    assert isinstance(feature_0.vertexes(), list)
    assert isinstance(feature_0.vertexes()[0], tuple)
    assert isinstance(feature_0.vertexes()[0][0], Time)
    assert isinstance(feature_0.vertexes()[0][1], float)
    assert feature_0.vertexes() == feature_data_0['vertexes']
    assert len(feature_0.vertexes()) == 6


def test_vertexes_unix(feature_0, feature_data_0):
    assert isinstance(feature_0.vertexes(unix_time=True)[0][0], float)


def test_coordinates(feature_0, feature_data_0):
    assert isinstance(feature_0._coordinates, list)
    assert feature_0._coordinates[0][0] == feature_data_0['vertexes'][0][0].unix
    assert feature_0._coordinates[0][1] == feature_data_0['vertexes'][0][1]
    assert LinearRing(feature_0._coordinates).is_ccw


def test_text_summary(feature_0):
    assert feature_0.to_text_summary == "some_feature1, 1141249646.0, 1141291505.0, 43.9369897680012, 1021.559655691171"


def test_tfcat_feature(feature_0):
    assert isinstance(feature_0.tfcat_feature(), TFCatFeature)


def test_tfcat_dict_multi_line_string(feature_0):
    assert isinstance(feature_0.to_tfcat_dict(), dict)
    assert feature_0.to_tfcat_dict()['type'] == "Feature"
    assert isinstance(feature_0.to_tfcat_dict()['geometry'], dict)
    assert feature_0.to_tfcat_dict()['geometry']['type'] == "MultiLineString"
    assert isinstance(feature_0.to_tfcat_dict()['geometry']['coordinates'], list)
    assert isinstance(feature_0.to_tfcat_dict()['properties'], dict)
    assert 'feature_type' in feature_0.to_tfcat_dict()['properties'].keys()
    assert 'id' in feature_0.to_tfcat_dict().keys()


def test_tfcat_dict_polygon(feature_1):
    assert feature_1.to_tfcat_dict()['geometry']['type'] == "Polygon"


def test__name(feature_0, feature_data_0):
    assert feature_0._name == feature_data_0['name']


def test__id(feature_0, feature_data_0):
    assert feature_0._id == feature_data_0['feature_id']


def test__time(feature_0, feature_data_0):
    assert isinstance(feature_0._time, Time)
    assert len(feature_0._time) == 6
    assert all(feature_0._time == [x[0] for x in feature_data_0['vertexes']])


def test__freq(feature_0,feature_data_0):
    assert isinstance(feature_0._freq, numpy.ndarray)
    assert len(feature_0._freq) == 6
    assert all(feature_0._freq == [x[1] for x in feature_data_0['vertexes']])


def test_arrays(feature_0):
    assert isinstance(feature_0.arrays(), tuple)
    assert all(feature_0.arrays()[0] == feature_0._time)
    assert all(feature_0.arrays()[1] == feature_0._freq)


def test_is_in_time_range(feature_0):
    assert feature_0.is_in_time_range(feature_0._time.min(), feature_0._time.max())
    assert not feature_0.is_in_time_range(
        feature_0._time.min() - 10*Unit('d'),
        feature_0._time.max() - 10*Unit('d')
    )


def test_crop(feature_1):
    bbox = (
        numpy.min(feature_1._time),
        numpy.min(feature_1._freq),
        numpy.max(feature_1._time),
        numpy.max(feature_1._freq),
    )
    coordinates = feature_1._coordinates
    feature_1.crop(bbox=bbox)
    assert feature_1._coordinates == pytest.approx(coordinates)


def test_crop_fmax_510(feature_1, coordinates_crop_fmax_510):
    bbox = (
        numpy.min(feature_1._time),
        numpy.min(feature_1._freq),
        numpy.max(feature_1._time),
        510,
    )
    feature_1.crop(bbox=bbox)
    assert feature_1._coordinates == pytest.approx(coordinates_crop_fmax_510)
