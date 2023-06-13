"""
This module contains tests for the function combine_grid_information on netcdf data.

Contains tests: test_wo_celldata, test_w_celldata, test_wrong_grid
"""

import pytest
import xarray as xr
from xarray.testing import assert_identical

import iconarray
from iconarray.backend.grid import WrongGridException

f_w_celldata1 = "data/example_data/nc/lfff01000000.nc"
f_w_celldata2 = "data/example_data/nc/lfff00000000z"
f_celldata_incomatible_w_grid = (
    "data/example_data/nc/my_exp1_atm_3d_ml_20180921T000000Z.nc"
)
f_grid = "data/example_data/grids/ICON-1E_DOM01.nc"


@pytest.mark.parametrize(
    "file,grid_file", [(f_w_celldata1, f_grid), (f_w_celldata2, f_grid)]
)
def test_w_celldata(file, grid_file):
    """
    Test the combine_grid_information function with a NETCDF file containing cell center variables.

    Ensure that grid information is correctly added.

    Parameters
    ----------
    file : str | Path
        Path to ICON data file.

    grid_file : str | Path
        Path to grid file.
    """
    ds_cell = iconarray.combine_grid_information(file, grid_file)

    ds_grid = iconarray.open_dataset(grid_file)

    assert "cell" in list(
        ds_cell.T.dims
    ), "ds_cell data variables should have a dimension 'cell'"
    assert (
        len(ds_cell.T.cell) == ds_grid.dims["cell"]
    ), f"ds_cell should have a dimension 'cell', with length {ds_grid.dims['cell']}."
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
    with pytest.raises(WrongGridException):
        iconarray.combine_grid_information(f_celldata_incomatible_w_grid, f_grid)


def test_grid_dataset_cell():
    """Test the API of combine_grid_information that passes a dataset instead of a filename."""
    ds_cell = xr.open_dataset(f_w_celldata1, engine="netcdf4")
    grid_ds = xr.open_dataset(f_grid, engine="netcdf4")

    ds_cell = iconarray.combine_grid_information(ds_cell, grid_ds)

    assert "cell" in list(
        ds_cell.T.dims
    ), "ds_cell data variables should have a dimension 'cell'"


def test_filter():
    """Test that we can filter a xarray.Dataset to a xarray.DataArray with a single variable."""
    ds_t = iconarray.open_dataset(f_w_celldata2, "T")

    ds = iconarray.open_dataset(f_w_celldata2)
    ds_t2 = iconarray.filter_by_var(ds, "T")

    assert_identical(ds_t, ds_t2)

    assert len(list(ds_t.data_vars)) == 1
    assert list(ds_t.data_vars)[0] == "T"


def test_var_not_found():
    """Test the output of vars available in the file if the requested var is not found."""
    ds = iconarray.open_dataset(f_w_celldata1)
    try:
        _ = iconarray.open_dataset(f_w_celldata1, "T_MISSING")
    except KeyError as e:
        assert all(
            [x in str(e) for x in ds.data_vars]
        ), "list of variables in files incorrect"
