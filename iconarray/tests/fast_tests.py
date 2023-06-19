"""A collection of fast tests."""

import codecs
from unittest.mock import Mock, mock_open

import pytest

from iconarray.backend.grid import _identify_datatype, _identifyGRIB, _identifyNC


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
    mocked_nc_data = mock_open(read_data="grib mocked data")
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
