"""A collection of fast tests."""

import codecs
from unittest.mock import Mock, mock_open, patch

import cfgrib
import numpy as np
import pytest
import xarray as xr

from iconarray.backend.grid import (
    WrongGridException,
    _add_cell_encoding,
    _add_edge_encoding,
    _identify_datatype,
    _identifyGRIB,
    _identifyNC,
    _open_GRIB,
    get_cell_dim_name,
    get_dim_names,
    get_edge_dim_name,
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


def _create_test_data(
    add_attrs: bool = True,
    ncells: int = 8,
    cell: str = "cell",
    nedges: int = 12,
    edge: str = "edge",
) -> xr.Dataset:
    rs = np.random.RandomState()
    _vars = {
        "T": [cell, "height"],
        "U": [edge, "height"],
        "V": [edge, "height"],
        "T_2M": [cell],
    }

    _dims = {cell: ncells, edge: nedges, "height": 10}

    obj = xr.Dataset()
    obj[cell] = (cell, np.arange(_dims[cell]))
    obj[edge] = (edge, np.arange(_dims[edge]))
    obj["height"] = ("height", 10 * np.arange(_dims["height"]))
    for v, dims in sorted(_vars.items()):
        data = rs.normal(size=tuple(_dims[d] for d in dims))
        obj[v] = (dims, data)
        if add_attrs:
            obj[v].attrs = {"foo": "variable"}

    assert all(obj.data.flags.writeable for obj in obj.variables.values())
    return obj


def _create_test_grid_data(cell: int = 8, edge: int = 12) -> xr.Dataset:
    rs = np.random.RandomState()

    _coords = {
        "clon": "cell",
        "clat": "cell",
        "elon": "edge",
        "elat": "edge",
    }

    _dims = {"cell": cell, "edge": edge}

    obj = xr.Dataset()

    for v, coord in sorted(_coords.items()):
        obj.coords[v] = (_coords[v], sorted(rs.random_sample(size=_dims[coord])))

    assert all(obj.data.flags.writeable for obj in obj.variables.values())
    return obj


@pytest.fixture
def data_simple():
    """Test dataset which matches the grid_data() fixture."""
    # noqa: DAR
    return _create_test_data()


@pytest.fixture
def data_with_diff_cell_name():
    """Test dataset which matches the grid_data() fixture but varying dimension names."""
    # noqa: DAR
    return _create_test_data(cell="values", edge="values2")


@pytest.fixture
def data_for_different_grid():
    """Test dataset which does not match the grid_data() fixture."""
    # noqa: DAR
    return _create_test_data(ncells=20, nedges=30)


@pytest.fixture
def grid_data():
    """Test grid dataset."""
    # noqa: DAR
    return _create_test_grid_data()


@pytest.mark.parametrize(
    "data,grid,expected",
    [
        ("data_simple", "grid_data", "cell"),
        ("data_with_diff_cell_name", "grid_data", "values"),
        ("data_for_different_grid", "grid_data", None),
    ],
)
def test_get_cell_dim_name(data, grid, expected, request):
    """Test that get_cell_dim_name returns the name of the edge dimension or None."""
    # noqa: DAR101
    data = request.getfixturevalue(data)
    grid_data = request.getfixturevalue(grid)
    cell = get_cell_dim_name(data, grid_data)

    assert cell == expected


@pytest.mark.parametrize(
    "data,grid,expected",
    [
        ("data_simple", "grid_data", "edge"),
        ("data_with_diff_cell_name", "grid_data", "values2"),
        ("data_for_different_grid", "grid_data", None),
    ],
)
def test_get_edge_dim_name(data, grid, expected, request):
    """Test get_edge_dim_name returns the name of cell dimension, or None."""
    # noqa: DAR101
    data = request.getfixturevalue(data)
    grid_data = request.getfixturevalue(grid)
    edge = get_edge_dim_name(data, grid_data)

    assert edge == expected


@pytest.mark.parametrize(
    "data,grid,expected",
    [
        ("data_simple", "grid_data", "cell,edge"),
        ("data_with_diff_cell_name", "grid_data", "values,values2"),
    ],
)
def test_get_dim_names(data, grid, expected, request):  # noqa: DAR101
    """Test that get_dim_names works as expected."""
    # noqa: DAR101
    data = request.getfixturevalue(data)
    grid_data = request.getfixturevalue(grid)
    cell, edge = get_dim_names(data, grid_data)

    assert cell == expected.split(",")[0]
    assert edge == expected.split(",")[1]


@pytest.mark.parametrize("data,grid", [("data_for_different_grid", "grid_data")])
def test_get_dim_names_exception(data, grid, request):
    """Test that get_dim_names raises WrongGridException if wrong grid is used."""
    # noqa: DAR101
    data = request.getfixturevalue(data)
    grid_data = request.getfixturevalue(grid)

    with pytest.raises(WrongGridException):
        cell, edge = get_dim_names(data, grid_data)


@pytest.mark.parametrize("data", [("data_simple")])
def test_add_cell_encoding(data, request):
    """Test that _add_cell_encoding ensures clon and clat in coordinate encoding."""
    # noqa: DAR101
    data = request.getfixturevalue(data)

    _add_cell_encoding(data["T"])
    assert all(
        x in data["T"].encoding["coordinates"].split(" ") for x in ["clon", "clat"]
    )


@pytest.mark.parametrize("data", [("data_simple")])
def test_add_edge_encoding(data, request):
    """Test that _add_edge_encoding ensures elon and elat in coordinate encoding."""
    # noqa: DAR101
    data = request.getfixturevalue(data)

    _add_edge_encoding(data["U"])
    assert all(
        x in data["U"].encoding["coordinates"].split(" ") for x in ["elon", "elat"]
    )


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



def test_dummy():
    assert 1 == 1
