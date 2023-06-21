"""A collection of fast tests."""

import codecs
from unittest.mock import Mock, mock_open, patch

import cfgrib
import pytest

from iconarray.backend.grid import (
    _identify_datatype,
    _identifyGRIB,
    _identifyNC,
    _open_GRIB,
)


@pytest.mark.parametrize(
    "file_nc,file_gb,expected",
    [(True, False, "nc"), (False, True, "grib"), (False, False, False)],
)
def test_identify_datatype(monkeypatch, file_nc, file_gb, expected):
    """Test _identify_datatype() with different inputs."""
    # noqa: DAR101
    _identifyNC = Mock()
    _identifyGRIB = Mock()
    _identifyNC.return_value = file_nc
    _identifyGRIB.return_value = file_gb

    monkeypatch.setattr("iconarray.backend.grid._identifyNC", _identifyNC)
    monkeypatch.setattr("iconarray.backend.grid._identifyGRIB", _identifyGRIB)

    assert _identify_datatype("file.whatever") == expected
    _identifyNC.assert_called_once()
    if expected != "nc":
        _identifyGRIB.assert_called_once()


@pytest.fixture
def mocker_open_isnc(mocker):
    """Mock codecs.open() for a netCDF file."""
    # noqa: DAR101
    mocked_nc_data = mock_open(read_data="CDF mocked nc data")
    mocker.patch("codecs.open", mocked_nc_data)


@pytest.fixture
def mocker_open_isgrib(mocker):
    """Mock codecs.open() for a GRIB file."""
    # noqa: DAR101
    mocked_nc_data = mock_open(read_data="GRIB mocked data")
    mocker.patch("codecs.open", mocked_nc_data)


@pytest.mark.parametrize(
    "open_mock,expected", [("mocker_open_isnc", True), ("mocker_open_isgrib", False)]
)
def test_identifyNC(open_mock, expected, request):
    """Test _identifyNC with two different mocked files."""
    # noqa: DAR101
    _ = request.getfixturevalue(open_mock)
    assert _identifyNC("file.nc") == expected
    codecs.open.assert_called_once()


@pytest.mark.parametrize(
    "open_mock,expected", [("mocker_open_isnc", False), ("mocker_open_isgrib", True)]
)
def test_identifyGRIB(open_mock, expected, request):
    """Test _identifyGRIB with two different mocked files."""
    # noqa: DAR101
    _ = request.getfixturevalue(open_mock)
    assert _identifyGRIB("file.grib") == expected
    codecs.open.assert_called_once()


@pytest.fixture
def mocker_open_gribfile(mocker):
    """Mock cfgrib.open_datasets()."""
    # noqa: DAR101
    mocked_gribfile = mock_open(read_data="grib mocked data")
    mocker.patch("cfgrib.open_datasets", mocked_gribfile)
    cfgrib.open_datasets.seide_effect = KeyError("paramId")


def test_open_GRIB_raise(mocker):
    """Test if _open_GRIB raises correclty."""  # noqa: DAR101
    mocked_gribfile = mock_open(read_data="grib mocked data")
    mocker.patch("cfgrib.open_datasets", mocked_gribfile)
    cfgrib.open_datasets.side_effect = KeyError("paramId")

    mocked_function = Mock()
    mocked_function.return_value = "var1, var2"

    with pytest.raises(KeyError) as e:
        with patch("iconarray.backend.grid.show_GRIB_shortnames", new=mocked_function):
            _open_GRIB(
                "file", "variable", decode_coords={}, decode_times={}, backend_kwargs={}
            )
    assert e.exconly().startswith('KeyError: "Cannot filter dataset by variable')

    cfgrib.open_datasets.side_effect = KeyError("else")
    with pytest.raises(KeyError) as e:
        with patch("iconarray.backend.grid.show_GRIB_shortnames", new=mocked_function):
            _open_GRIB(
                "file", "variable", decode_coords={}, decode_times={}, backend_kwargs={}
            )
    assert e.exconly() == "KeyError: 'else'"
