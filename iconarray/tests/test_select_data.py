"""
This module contains tests for the function select_data().

Contains tests: test_file, test_ds, test_getall, test_with_grid
"""

import iconarray

file_native = "./data/example_data/grib/lfff00000000z_vn"  # unstructured grid
file_latlon = "./data/example_data/grib/i1effsurf000_001"  # latlon grid
file_nc = "./data/example_data/nc/icon_19790101T000000Z.nc"  # netcdf unstructured grid
file_grid = "./data/example_data/grids/domain1_DOM01_r19b07.nc"


def test_file():
    """
    Test the select_data() function with existing and non-existing variables.

    The variables are selected from different hypercubes. Tests are performed using
    file paths as input for select_data().
    """
    # grib unstructured grid
    variables = ["T", "CLAT", "CLON", "BLUE"]
    ds_dict = iconarray.select_data(file_native, variables)
    assert sorted(list(ds_dict.keys())) == [
        "CLAT",
        "CLON",
        "T",
    ], "ds_dict should have the variables ['CLAT', 'CLON', 'T']"
    assert (
        type(ds_dict["T"]).__name__ == "DataArray"
    ), "type name of ds_dict['T'] should be DataArray"

    # grib latlon grid
    variables = ["T", "CAPE_ML", "CIN_ML", "BLUE"]
    ds_dict = iconarray.select_data(file_latlon, variables)
    assert sorted(list(ds_dict.keys())) == [
        "CAPE_ML",
        "CIN_ML",
        "T",
    ], "ds_dict should have the variables ['CAPE_ML', 'CIN_ML', 'T']"
    assert (
        type(ds_dict["T"]).__name__ == "DataArray"
    ), "type name of ds_dict['T'] should be DataArray"

    # netcdf unstructured grid
    variables = ["temp", "t_so", "BLUE"]
    ds_dict = iconarray.select_data(file_nc, variables)
    assert sorted(list(ds_dict.keys())) == [
        "t_so",
        "temp",
    ], "ds_dict should have the variables ['t_so', 'temp']"
    assert (
        type(ds_dict["temp"]).__name__ == "DataArray"
    ), "type name of ds_dict['temp'] should be DataArray"


def test_ds():
    """
    Test the select_data() function with existing and non-existing variables.

    The variables are selected from different hypercubes. Tests are performed using
    the open_dataset() to first read the data and calling select_data() on the
    output.
    """
    # grib unstructured grid
    variables = ["T", "CLAT", "CLON", "BLUE"]
    ds = iconarray.open_dataset(file_native)
    ds_dict = iconarray.select_data(ds, variables)
    assert sorted(list(ds_dict.keys())) == [
        "CLAT",
        "CLON",
        "T",
    ], "ds_dict should have the variables ['CLAT', 'CLON', 'T']"
    assert (
        type(ds_dict["T"]).__name__ == "DataArray"
    ), "type name of ds_dict['T'] should be DataArray"

    # grib latlon grid
    variables = ["T", "CAPE_ML", "CIN_ML", "BLUE"]
    ds = iconarray.open_dataset(file_latlon)
    ds_dict = iconarray.select_data(ds, variables)
    assert sorted(list(ds_dict.keys())) == [
        "CAPE_ML",
        "CIN_ML",
        "T",
    ], "ds_dict should have the variables ['CAPE_ML', 'CIN_ML', 'T']"
    assert (
        type(ds_dict["T"]).__name__ == "DataArray"
    ), "type name of ds_dict['T'] should be DataArray"

    # netcdf unstructured grid
    variables = ["temp", "t_so", "BLUE"]
    ds = iconarray.open_dataset(file_nc)
    ds_dict = iconarray.select_data(ds, variables)
    assert sorted(list(ds_dict.keys())) == [
        "t_so",
        "temp",
    ], "ds_dict should have the variables ['t_so', 'temp']"
    assert (
        type(ds_dict["temp"]).__name__ == "DataArray"
    ), "type name of ds_dict['temp'] should be DataArray"


def test_getall():
    """Test the select_data() function to select all variables in the file."""
    # grib unstructured grid
    variables = []
    ds_dict = iconarray.select_data(file_native, variables)
    assert sorted(list(ds_dict.keys())) == [
        "CLAT",
        "CLON",
        "ELAT",
        "ELON",
        "T",
        "U",
        "V",
        "VLAT",
        "VLON",
    ], "ds_dict should have the variables ['CLAT', 'CLON', 'ELAT', 'ELON', 'T', 'U', 'V', 'VLAT', 'VLON']"


def test_with_grid():
    """
    Test the select_data() function with specification of a grid file.

    The test also tests if the specify variable can be a string.
    """
    # grib unstructured grid
    variables = "T"
    ds_dict = iconarray.select_data(file_native, variables, grid_file=file_grid)
    assert (
        sum([1 for coord in ["clon", "clat"] if coord in ds_dict["T"].coords]) == 2
    ), "ds_dict should have coordinates 'clon', 'clat'"
