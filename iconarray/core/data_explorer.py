"""
The data_explorer.py module contains various functions useful for inspecting (ICON) data.

Contains public functions: show_data_vars, data_inspect
"""

import logging
import six
import xarray
import pandas as pd
import sys


# show_data_vars can be used in python scripts to find out which variable name psyplot will need to plot that variable.
# eg if GRIB_cfVarName is defined, cfgrib will set this as the variable name, as opposed to GRIB_shortName.
def show_data_vars(ds):
    """
    Print a table with variables in dataset.

    The first column is the variable name chosen by cfgrib to use eg. when plotting with psyplot.

    Parameters
    ----------
    ds : xarray.Dataset
        Dataset of ICON GRIB data opened with cgrib engine or cfgrib.
    """
    if type(ds) is str:
        Exception(
            "Argument is not a Dataset. Please open the dataset via psy.open_dataset() and pass returned Dataset to this function."
        )
    elif type(ds) is xarray.core.dataset.Dataset:
        print(
            "{:<15} {:<32} {:<20} {:<20} {:<10}".format(
                "psyplot name", "long_name", "GRIB_cfVarName", "GRIB_shortName", "units"
            )
        )
        for _k, v in six.iteritems(ds.data_vars):
            i = ds.data_vars[v.name]
            try:
                long_name = (
                    (i.long_name[:28] + "..") if len(i.long_name) > 28 else i.long_name
                )
            except Exception:
                long_name = ""
            try:
                units = i.units
            except Exception:
                units = ""
            try:
                gribcfvarName = i.GRIB_cfVarName
            except Exception:
                gribcfvarName = ""
            try:
                gribshortName = i.GRIB_shortName
            except Exception:
                gribshortName = ""
            print(
                "{:<15} {:<32} {:<20} {:<20} {:<10}".format(
                    v.name, long_name, gribcfvarName, gribshortName, units
                )
            )


def data_inspect(ds):
    """
    Print an inventory of all hypercubes obtained from iconarray.open_datasets().

    This is currently only implemented for data from GRIB files.

    Parameters
    ----------
    ds : xarray.Dataset or List(xarray.Datasets)

    """
    # make sure input is iterable
    if not isinstance(ds, list):
        ds = [ds]

    for i, single_ds in enumerate(ds):
        print("=========================")
        print(f"Hypercube {i}")
        print("---")

        if "GRIB_edition" in single_ds.attrs:
            _print_grib_info(single_ds)
        else:
            try:
                _print_nc_info(single_ds)
            except KeyError as e:
                logging.error("Unknown data structure.")
                sys.exit(e)


def _print_grib_info(ds):
    """Print hypercube and variable infos for data from a GRIB file.

    Parameters
    ----------
    ds : xarray.Dataset
    """
    for i, (vname, vdata) in enumerate(ds.data_vars.items()):

        # variable independent info of the hypercube
        if i == 0:
            try:
                lt = vdata.attrs["GRIB_typeOfLevel"]
                vt = vdata.coords["valid_time"].values
                vt_str = pd.to_datetime(str(vt)).strftime("%Y-%m-%d %H:%M:%S")
                dt = vdata.attrs["GRIB_dataType"]
                gt = vdata.attrs["GRIB_gridType"]
                # print hypercube infos
                print(f"dataType         : {dt}")
                print(f"gridType         : {gt}")
                print(f"shape of grid    : {vdata.shape}")
                print(f"typeOfLevel      : {lt}")
                print(f"number of levels : {vdata.coords[lt].size}")
                print(f"valid time       : {vt_str}")
                print("---")
                print("variables (shortName, cfName, cfVarName, name, units)")
            except KeyError as e:
                logging.warn("Missing hypercube info in the data: %s", e)

        # variable dependent information
        try:
            cf_n = vdata.attrs["GRIB_cfName"]
            cf_vn = vdata.attrs["GRIB_cfVarName"]
            name = vdata.attrs["GRIB_name"]
            units = vdata.attrs["GRIB_units"]
            # print variables infos
            print(f"   {vname[:10]:<10} {cf_n[:40]:<40} {cf_vn[:10]:<10} {name[:50]:<50} {units}")
        except KeyError as e:
            logging.error("Missing variable info in the data.")
            sys.exit(e)


def _print_nc_info(ds):
    """Print hypercube and variable infos for data from a netCDF file.

    Parameters
    ----------
    ds : xarray.Dataset
    """
    for i, (vname, vdata) in enumerate(ds.data_vars.items()):

        # variable independent info of the hypercube
        if i == 0:
            try:
                vt = vdata.coords["time"].values[0]
                vt_str = pd.to_datetime(str(vt)).strftime("%Y-%m-%d %H:%M:%S")
                gt = vdata.attrs["CDI_grid_type"]
                # print hypercube infos
                print(f"gridType         : {gt}")
                print(f"shape of grid    : {vdata.shape}")
                print(f"valid time       : {vt_str}")
                print("---")
                print("variables (var name, standard_name, name, units)")
            except KeyError as e:
                logging.warn("Missing hypercube info in the data: %s", e)

        # variable dependent information
        try:
            std_n = vdata.attrs["standard_name"]
            name = vdata.attrs["long_name"]
            try:
                units = vdata.attrs["units"]
            except KeyError:
                units = "/"
            # print variables infos
            print(f"   {vname[:10]:<10} {std_n[:40]:<40} {name[:50]:<50} {units}")
        except KeyError as e:
            logging.error("Missing variable info in the data.")
            sys.exit(e)
