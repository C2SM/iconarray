"""
This module contains tests for the function combine_grid_information on grib data.

Contains tests: test_grid_edge, test_grid_cell
"""

import itertools

import cfgrib
import pytest
import xarray as xr
from xarray.testing import assert_identical

import iconarray

f_vt_vn = "data/example_data/grib/vnvt00010000"  # ONLY VN, VT variables
f_alldata = "data/example_data/grib/lfff00010000_edgeplots"  # VN, VT AND cell center variables (P, T, U, V etc)
f_grid = "data/example_data/grids/icon_grid_0001_R19B08_mch.nc"  # GRID file


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
    ds_cell = dss[0]
    ds_edge = dss[1]
    return ds_cell, ds_edge


ds_cell, ds_edge = _open_file(f_alldata)


@pytest.mark.parametrize("ds_edge", [(ds_edge)])
def test_grid_edge(ds_edge):
    """
    Test the combine_grid_information function with a GRIB file containing both edge and cell center variables.

    Ensure that edge varialbes are extracted to ds_edge and grid information is correctly added.

    Parameters
    ----------
    ds_edge : xr.Dataset
        dataset containing only variables defined on the grid edge.
    """
    ds_edgevars = iconarray.combine_grid_information(ds_edge, f_grid)

    ds_grid = iconarray.open_dataset(f_grid)

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
    assert (
        sum(
            [
                1
                for coord in ["elon", "elat", "elon_bnds", "elat_bnds"]
                if coord in ds_edgevars.coords
            ]
        )
        == 4
    ), "ds_edgevars should have coordinates 'elon', 'elat', 'elon_bnds', 'elat_bnds'"


@pytest.mark.parametrize("ds_cell", [(ds_cell)])
def test_grid_cell(ds_cell):
    """
    Test the combine_grid_information function with a GRIB file containing both edge and cell center variables.

    Ensure that cell varialbes are extracted to ds_cell and grid information is correctly added.

    Parameters
    ----------
    ds_cell : xr.Dataset
        dataset containing only variables defined on the grid cell center.
    """
    ds_cellvars = iconarray.combine_grid_information(ds_cell, f_grid)

    ds_grid = iconarray.open_dataset(f_grid)

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
    assert (
        sum(
            [
                1
                for coord in ["clon", "clat", "clon_bnds", "clat_bnds"]
                if coord in ds_cellvars.coords
            ]
        )
        == 4
    ), "ds_cellvars should have coordinates 'clon', 'clat', 'clon_bnds', 'clat_bnds'"


@pytest.mark.parametrize("ds_cell", [(ds_cell)])
def test_grid_dataset_cell(ds_cell):
    """
    Test the API of combine_grid_information that passes a dataset instead of a filename.

    Parameters
    ----------
    ds_cell : xr.Dataset
        dataset containing only variables defined on the grid cell center.
    """
    grid_ds = xr.open_dataset(f_grid, engine="netcdf4")

    ds_cellvars = iconarray.combine_grid_information(ds_cell, grid_ds)

    assert "cell" in list(
        ds_cellvars.P.dims
    ), "ds_cellvars data variables should have a dimension 'cell'"


def test_filter():
    """Test that we can filter a xarray.Dataset to a xarray.DataArray with a single variable."""
    ds_t = iconarray.open_dataset(f_alldata, "T")

    ds = iconarray.open_dataset(f_alldata)
    ds_t2 = iconarray.filter_by_var(ds, "T")

    assert_identical(ds_t, ds_t2)

    assert len(list(ds_t.data_vars)) == 1
    assert list(ds_t.data_vars)[0] == "T"


def test_var_not_found():
    """Test the output of vars available in the file if the requested var is not found."""
    ds = iconarray.open_dataset(f_alldata)
    var_list = list(itertools.chain.from_iterable([list(sds.keys()) for sds in ds]))
    try:
        _ = iconarray.open_dataset(f_alldata, "T_MISSING")
    except KeyError as e:
        assert all(
            [x in str(e) for x in var_list]
        ), "list of variables in files incorrect"
