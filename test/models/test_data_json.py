# -*- coding: utf-8 -*-
"""Test SPACE Labelling Tool test data."""
import pytest

from spacelabel import SCHEMA_URI
from tfcat.validate import validate_file
from pathlib import Path
from jsonschema.exceptions import ValidationError


@pytest.fixture
def schema():
    return SCHEMA_URI


@pytest.fixture
def tfcat_data_file():
    return Path(__file__).parent / "tfcat_data.json"


def test_tfcat_data(schema, tfcat_data_file):
    try:
        validate_file(tfcat_data_file, schema_uri=schema)
    except ValidationError:
        pytest.fail("Validation Error")