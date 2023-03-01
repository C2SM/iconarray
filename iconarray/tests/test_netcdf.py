"""
This module contains tests for the function combine_grid_information on netcdf data.

Contains tests: test_wo_celldata, test_w_celldata, test_wrong_grid
"""

import pytest
import xarray as xr
from xarray.testing import assert_identical

import iconarray
from iconarray.backend import grid

f_wo_celldata = "data/example_data/nc/lfff01000000.nc"
f_w_celldata = "data/example_data/nc/lfff00000000z"
f_celldata_incomatible_w_grid = (
    "data/example_data/nc/my_exp1_atm_3d_ml_20180921T000000Z.nc"
)
f_grid = "data/example_data/grids/ICON-1E_DOM01.nc"


def test_wo_celldata():
    """
    Test the combine_grid_information function with a NETCDF file containing cell center variables.

    Ensure that grid information is correctly added.
    """
    ds_cell = iconarray.combine_grid_information(f_wo_celldata, f_grid)

    assert "cell" in list(
        ds_cell.T.dims
    ), "ds_cell data variables should have a dimension 'cell'"
    assert (
        len(ds_cell.T.cell) == 1028172
    ), "ds_cell should have a dimension 'cell', with length 1028172."
    assert (
        sum(
            [
                1
                for coord in ["clon", "clat", "clon_bnds", "clat_bnds"]
                if coord in ds_cell.coords
            ]
        )
        == 4
    ), "ds_cell should have coordinates 'clon', 'clat', 'clon_bnds', 'clat_bnds'"


def test_w_celldata():
    """
    Test the combine_grid_information function with a NETCDF file containing cell center variables.

    Ensure that grid information is correctly added.
    """
    ds_cell = iconarray.combine_grid_information(f_w_celldata, f_grid)

    assert "cell" in list(
        ds_cell.T.dims
    ), "ds_cell data variables should have a dimension 'cell'"
    assert (
        len(ds_cell.T.cell) == 1028172
    ), "ds_cell should have a dimension 'cell', with length 1028172."
    assert (
        sum(
            [
                1
                for coord in ["clon", "clat", "clon_bnds", "clat_bnds"]
                if coord in ds_cell.coords
            ]
        )
        == 4
    ), "ds_cell should have coordinates 'clon', 'clat', 'clon_bnds', 'clat_bnds'"


def test_wrong_grid():
    """Test that combine_grid_information raises an error when trying to add the data from an incorrect grid to data from a NETCDF file."""
    with pytest.raises(grid.WrongGridException):
        iconarray.combine_grid_information(f_celldata_incomatible_w_grid, f_grid)


def test_grid_dataset_cell():
    """Test the API of combine_grid_information that passes a dataset instead of a filename."""
    ds_cell = xr.open_dataset(f_wo_celldata, engine="netcdf4")
    grid_ds = xr.open_dataset(f_grid, engine="netcdf4")

    ds_cell = iconarray.combine_grid_information(ds_cell, grid_ds)

    assert "cell" in list(
        ds_cell.T.dims
    ), "ds_cell data variables should have a dimension 'cell'"


def test_filter():
    """Test that we can filter a xarray.Dataset to a xarray.DataArray with a single variable."""
    ds_t = iconarray.open_dataset(f_w_celldata, "T")

    ds = iconarray.open_dataset(f_w_celldata)
    ds_t2 = iconarray.filter_by_var(ds, "T")

    assert_identical(ds_t, ds_t2)

    assert len(list(ds_t.data_vars)) == 1
    assert list(ds_t.data_vars)[0] == "T"


def test_var_not_found():
    """Test the output of vars available in the file if the requested var is not found."""
    ds = iconarray.open_dataset(f_wo_celldata)
    try:
        _ = iconarray.open_dataset(f_wo_celldata, "T_MISSING")
    except KeyError as e:
        assert ", ".join(ds.data_vars) in str(e), "list of variables in files incorrect"
