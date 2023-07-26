"""A collection of tests with a dependency on example data."""

import pytest

from iconarray.backend.grid import _identify_datatype

grib_file = "data/example_data/grib/lfff00000000"
nc_file = "data/example_data/nc/icon_19790101T000000Z.nc"
# txt_file = "data/example_data/test.txt"  # noqa: E800


@pytest.mark.parametrize(
    "file_name,expected",
    #    [(nc_file, "nc"), (grib_file, "grib"), (txt_file, False)],  # noqa: E800
    [(nc_file, "nc"), (grib_file, "grib")],
)
def test_identify_datatype(file_name, expected):
    """Test _identify_datatype() with different input files."""
    # noqa: DAR101
    assert _identify_datatype(file_name) == expected
