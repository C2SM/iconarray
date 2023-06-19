"""A collection of fast tests."""

from unittest.mock import Mock

import pytest

from iconarray.backend.grid import _identify_datatype

# Questions and ideas
#
# would it be possible to mock fd or fdata in _identifyNC?
# or would that need a new function fdata = ...?
# mock fd somehow?


@pytest.mark.parametrize(
    "file_nc,file_gb,expected",
    [(True, False, "nc"), (False, True, "grib"), (False, False, False)],
)
def test_identify_datatype(monkeypatch, file_nc, file_gb, expected):
    """Test the return of _identify_datatype() with different inputs."""
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
