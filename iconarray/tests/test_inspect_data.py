"""
This module contains tests for the function inspect_data().

Contains tests: test_inspect_data
"""

import iconarray

file_native = "./data/example_data/grib/lfff00000000z_vn"  # GRIB unstructured grid
file_nc = "./data/example_data/nc/icon_19790101T000000Z.nc"  # netcdf unstructured grid


def test_inspect_data():
    """
    Test the insepct_data() function.

    Just test if it does not throw exceptions with a GRIB and a netCDF file.
    """
    # testing automatically fails if an exception is raised
    # test with GRIB
    ds = iconarray.open_dataset(file_native)
    iconarray.inspect_data(ds)
    # test with netCDF
    ds = iconarray.open_dataset(file_nc)
    iconarray.inspect_data(ds)
