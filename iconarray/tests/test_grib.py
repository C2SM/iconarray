"""
This module contains tests for the function combine_grid_information on grib data.

Contains tests: test_grid_edge, test_grid_cell
"""

import itertools

import cfgrib
import pytest
import xarray as xr
from xarray.testing import assert_identical

from iconarray import combine_grid_information, open_dataset, filter_by_var
from iconarray.backend.grid import _identify_datatype, _open_GRIB


f_vt_vn = "data/example_data/grib/vnvt00010000"  # ONLY VN, VT variables
f_alldata = "data/example_data/grib/lfff00010000_edgeplots"  # VN, VT AND cell center variables (P, T, U, V etc)
f_grid = "data/example_data/grids/icon_grid_0001_R19B08_mch.nc"  # GRID file

f_alldata_cropped = "data/example_data/grib/lfff00010000_edgeplots_cropped"  # VN, VT AND cell center variables (P, T, U, V etc)
f_grid_cropped = "data/example_data/grids/icon_grid_0001_R19B08_mch.nc"  # GRID file

def _open_file(data):
    dss = cfgrib.open_datasets(
        data,
        engine="cfgrib",
        backend_kwargs={
            "indexpath": "",
            "errors": "ignore",
            "read_keys": ["typeOfLevel", "gridType"],
            "filter_by_keys": {"typeOfLevel": "generalVerticalLayer"},
        },
        encode_cf=("time", "geography", "vertical"),
    )
    ds_cell, ds_edge = dss
    return ds_cell, ds_edge


@pytest.fixture(scope="module")
def alldata():
    """
    Fixture that provides tests with cell and edge datasets of GRIB file.

    Returns
    ----------
    [ds_cell,ds_edge] : tuple[xr.Dataset,xr.Dataset]
    """
    ds_cell, ds_edge = _open_file(f_alldata)
    return ds_cell, ds_edge


def test_grid_edge(alldata):
    """
    Test the combine_grid_information function with a GRIB file containing both edge and cell center variables.

    Ensure that edge variables are extracted to ds_edge and grid information is correctly added.

    Parameters
    ----------
    alldata : tuple[xr.Dataset,xr.Dataset]
        dataset containing variables defined on the grid cell and edge.
    """
    _, ds_edge = alldata
    ds_edge = ds_edge.copy()

    ds_edgevars = combine_grid_information(ds_edge, f_grid)

    ds_grid = open_dataset(f_grid)

    assert list(ds_edgevars.data_vars) == [
        "VN",
        "VT",
    ], "ds_edgevars should only have two data variables, ['VN', 'VT']"
    assert (
        len(ds_edgevars.edge.values) == ds_grid.dims["edge"]
    ), f"ds_edgevars should have a dimension edge, with length {ds_grid.dims['edge']}."
    assert "edge" in list(
        ds_edgevars.VN.dims
    ), "ds_edgevars data variables should have a dimension edge"
    assert ds_edgevars.coords.keys() >= {
        "elon",
        "elat",
        "elon_bnds",
        "elat_bnds",
    }, "ds_edgevars should have coordinates 'elon', 'elat', 'elon_bnds', 'elat_bnds'"


def test_grid_cell(alldata):
    """
    Test the combine_grid_information function with a GRIB file containing both edge and cell center variables.

    Ensure that cell variables are extracted to ds_cell and grid information is correctly added.

    Parameters
    ----------
    alldata : tuple[xr.Dataset,xr.Dataset]
        dataset containing variables defined on the grid cell and edge.
    """
    ds_cell, _ = alldata
    ds_cell = ds_cell.copy()

    ds_cellvars = combine_grid_information(ds_cell, f_grid)

    ds_grid = open_dataset(f_grid)

    assert list(ds_cellvars.data_vars) == [
        "P",
        "T",
        "U",
        "V",
        "QV",
        "QC",
        "QI",
    ], "ds_cellvars should only have two data variables, ['P', 'T', 'U', 'V', 'QV', 'QC', 'QI']"
    assert (
        len(ds_cellvars.cell.values) == ds_grid.dims["cell"]
    ), f"ds_cellvars should have a dimension 'cell', with length {ds_grid.dims['cell']}."
    assert "cell" in list(
        ds_cellvars.P.dims
    ), "ds_cellvars data variables should have a dimension 'cell'"
    assert ds_cellvars.coords.keys() >= {
        "clon",
        "clat",
        "clon_bnds",
        "clat_bnds",
    }, "ds_cellvars should have coordinates clon', 'clat', 'clon_bnds', 'clat_bnds'"


def test_grid_dataset_cell(alldata):
    """
    Test the API of combine_grid_information that passes a dataset instead of a filename.

    Parameters
    ----------
    alldata : tuple[xr.Dataset,xr.Dataset]
        dataset containing variables defined on the grid cell and edge.
    """
    grid_ds = xr.open_dataset(f_grid, engine="netcdf4")

    ds_cell, _ = alldata
    ds_cell = ds_cell.copy()

    ds_cellvars = combine_grid_information(ds_cell, grid_ds)

    assert "cell" in list(
        ds_cellvars.P.dims
    ), "ds_cellvars data variables should have a dimension 'cell'"

@pytest.mark.parametrize(
    "file",
    [
        (f_alldata),
        (f_alldata_cropped),
    ],
)
def test_filter(file):
    """Test that we can filter a xarray.Dataset to a xarray.DataArray with a single variable."""
    ds_t = open_dataset(file, "T")

    ds = open_dataset(file)
    ds_t2 = filter_by_var(ds, "T")

    assert_identical(ds_t, ds_t2)

    assert len(list(ds_t.data_vars)) == 1
    assert list(ds_t.data_vars)[0] == "T"

def test_open_GRIB_raise():
    """Test if _open_GRIB raises correclty with input file."""  # noqa: DAR101
    grib_file = "data/example_data/grib/lfff00000000"
    with pytest.raises(KeyError) as e:
        _open_GRIB(
            grib_file, "var", decode_coords={}, decode_times={}, backend_kwargs={}
        )
    assert e.exconly().startswith('KeyError: "Cannot filter dataset by variable')


def test_var_not_found():
    """Test the output of vars available in the file if the requested var is not found."""
    ds = open_dataset(f_alldata)
    var_list = list(itertools.chain.from_iterable([list(sds.keys()) for sds in ds]))
    try:
        _ = open_dataset(f_alldata, "T_MISSING")
    except KeyError as e:
        assert all(
            [x in str(e) for x in var_list]
        ), "list of variables in files incorrect"

        

