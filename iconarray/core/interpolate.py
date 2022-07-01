"""The functions in interpolate.py are used to facilitate the interpolation of ICON vector data to a regular grid, or a coarser ICON grid, for the purpose of vectorplots, e.g., wind plots. For psyplot we recommend to plot wind data on the regular grid as you can then scale the density of arrows in a vector plot as desired."""

import os
import subprocess
from pathlib import Path

# ----------------------------------------------------------------------
#
# functions and definitions for ICON grid A to Regular grid interpolation
# via fieldextra
#
# ----------------------------------------------------------------------

iconremap_namelist = """
!*********************************************************************************************
! Namelist for remapping ICON grid to {gridtype}
! Usage: fieldextra remap.nl
!        where fieldextra points to /project/s83c/fieldextra/tsa/bin/fieldextra_gnu_opt_omp
!        or /project/s83c/fieldextra/daint/bin/fieldextra_gnu_opt_omp
!*********************************************************************************************
!!!! HEADER
! Global settings
&RunSpecification
 verbosity             = "high"
 additional_diagnostic = .true.
 n_ompthread_total = 6
/
&GlobalResource
 dictionary            = "/project/s83c/fieldextra/tsa/resources/dictionary_icon.txt"
 grib_definition_path  = "/project/s83c/fieldextra/tsa/resources/eccodes_definitions_cosmo",
                         "/project/s83c/fieldextra/tsa/resources/eccodes_definitions_vendor"
 grib2_sample          = "/project/s83c/fieldextra/tsa/resources/eccodes_samples/COSMO_GRIB2_default.tmpl"
 icon_grid_description = '{in_grid_file}',
                         '{out_grid_file}'
/
&GlobalSettings
 default_model_name            = "icon"
 default_product_category      = "determinist"
 default_out_type_stdlongitude = .true.
/
! Model specifc information
&ModelSpecification
 model_name            = "icon"
 regrid_method         = "icontools,rbf",
/
! Information associated to imported NetCDF file
&NetCDFImport
 dim_default_attribute = "ncells:long_name=unstructured_grid_cell_index value=index",
                         "alt: axis=z standard_name=height",
 {varname_translation}
/
!!!! PRODUCT
&Process
  in_file='{data_file}'
  out_file='{file_out}', out_type="NETCDF",
  out_regrid_target = '{out_regrid_options}'
  out_regrid_method = "default"
  in_size_vdate = {num_dates}
  out_type_nccoordbnds = .true.
/
&Process in_field = "U" /
&Process in_field = "V" /
"""


def _create_remap_nl(
    gridtype,
    remap_namelist_path,
    data_file,
    file_out,
    num_dates,
    out_regrid_options,
    in_grid_file,
    out_grid_file="",
):
    """
    Create REMAP namelist for Fieldextra remapping.

    See fieldextra documentation for more information on the namelists.
    https://github.com/COSMO-ORG/fieldextra

    Parameters
    ----------
    gridtype : str
        'icon' or 'regular'
    remap_namelist_path : Path
        Output path to save namelist file.
    data_file : Path
        Path to ICON data.
    file_out : Path
        Output path for interpolated ICON data.
    num_dates : integer
        Number of time steps in data.
    out_regrid_options : str
        Information on output grid. See fieldextra documentation.
    in_grid_file : Path
        Path to original grid of ICON data.
    out_grid_file : Path
        Path to new grid to interpolate data to.
        In case of interpolating to regular grid, this defaults to "".

    Raises
    ----------
    Exception
        gridtype must be either 'icon' or 'regular', otherwise an exception is raised.
    """
    if gridtype == "icon":
        varname_translation = ""
        gridtype = "another (coarser) ICON Grid."
    elif gridtype == "regular":
        varname_translation = '''varname_translation   = "clon_bnds:__IGNORE__", "clat_bnds:__IGNORE__",
                         "clon:__IGNORE__", "clat:__IGNORE__"'''
        gridtype = "a regular grid."
    else:
        raise Exception("Only interpolates to ICON or regular grid.")

    with open(remap_namelist_path, "w") as f:
        f.write(
            iconremap_namelist.format(
                data_file=data_file,
                in_grid_file=in_grid_file,
                file_out=file_out,
                num_dates=num_dates,
                out_regrid_options=out_regrid_options,
                out_grid_file=out_grid_file,
                varname_translation=varname_translation,
                gridtype=gridtype,
            )
        )
    print("\nFieldextra Namelist saved to:" + os.path.abspath(remap_namelist_path))


def remap_ICON_to_regulargrid(data_file, in_grid_file, num_dates, region="CH"):
    """
    REMAP ICON data to regular grid using Fieldextra.

    This calls the _create_remap_nl() function to create a fieldextra
    namelist with your datafile, and subsequently runs fieldextra with this namelist.
    The path to fieldextra executable is taken from the environment variable: FIELDEXTRA_PATH.
    The output file along with a LOG and the namelist are saved in a tmp folder.
    The function returns the file location of the output file.

    See fieldextra documentation for more information on fieldextra.
    https://github.com/COSMO-ORG/fieldextra


    Parameters
    ----------
    data_file : Path
        Path to ICON data.
    num_dates : integer
        Number of time steps in data.
    in_grid_file : Path
        Path to original grid file of the ICON data.
    region : str
        Switzerland or Europe. Defaults to Swizerland.

    Returns
    ----------
    file_out : Path
        Path to resulting interpolated data.
    """
    remap_namelist_fname = "NAMELIST_ICON_REG_REMAP"
    output_dir = Path(os.path.abspath(Path("./tmp/fieldextra")))
    remap_namelist_path = output_dir / remap_namelist_fname
    file_out = output_dir / (Path(data_file).stem + "_interpolated_regulargrid.nc")

    data_file = os.path.abspath(data_file)
    in_grid_file = os.path.abspath(in_grid_file)
    file_out = os.path.abspath(file_out)

    # Create tmp directory for results and namelist
    output_dir.mkdir(parents=True, exist_ok=True)

    if str(region).lower() in ["swizerland", "ch"]:
        print("Creating regular grid over Switzerland region.")
        out_regrid_options = "geolatlon,5500000,45500000,11000000,48000000,55000,25000"
    elif str(region).lower() in "europe":
        print("Creating regular grid over Europe region.")
        out_regrid_options = "geolatlon,0,40000000,20000000,50000000,200000,100000"
    else:
        print("Creating regular grid over Switzerland region.")
        out_regrid_options = "geolatlon,5500000,45500000,11000000,48000000,55000,25000"

    # Create namelist
    _create_remap_nl(
        "regular",
        remap_namelist_path,
        data_file,
        file_out,
        num_dates,
        out_regrid_options,
        in_grid_file,
    )

    # Run fieldextra and save LOG file
    with open(output_dir / "LOG_ICON_REG_REMAP.txt", "w") as f:
        _log_fx(f, remap_namelist_path)

    with open(output_dir / "LOG_ICON_REG_REMAP.txt", "r") as f:
        _print_status(f, output_dir, file_out)

    return file_out


def remap_ICON_to_ICON(data_file, in_grid_file, out_grid_file, num_dates):
    """
    Remap ICON data to another ICON grid using Fieldextra.

    This calls the _create_remap_nl() function to create a fieldextra
    namelist with your datafile, and subsequently runs fieldextra with this namelist.
    The path to fieldextra executable is taken from the environment variable: FIELDEXTRA_PATH.
    The output file along with a LOG and the namelist are saved in a tmp folder.
    The function returns the file location of the output file.

    See fieldextra documentation for more information on fieldextra.
    https://github.com/COSMO-ORG/fieldextra


    Parameters
    ----------
    data_file : Path
        Path to ICON data.
    num_dates : integer
        Number of time steps in data.
    in_grid_file : Path
        Path to original grid file of the ICON data.
    out_grid_file : Path
        Path to new grid to interpolate data to.
        In case of interpolating to regular grid, this defaults to "".

    Returns
    ----------
    file_out : Path
        Path to resulting interpolated data.
    """
    remap_namelist_fname = "NAMELIST_ICON_ICON_REMAP"
    output_dir = Path("./tmp/fieldextra")
    remap_namelist_path = output_dir / remap_namelist_fname
    file_out = output_dir / (Path(data_file).stem + "_interpolated_ICONgrid.nc")

    data_file = os.path.abspath(data_file)
    in_grid_file = os.path.abspath(in_grid_file)
    out_grid_file = os.path.abspath(out_grid_file)
    file_out = os.path.abspath(file_out)

    out_regrid_options = "icon_grid,cell," + str(out_grid_file)
    # Create tmp directory for results and namelist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create namelist
    _create_remap_nl(
        "icon",
        remap_namelist_path,
        data_file,
        file_out,
        num_dates,
        out_regrid_options,
        in_grid_file,
        out_grid_file,
    )

    # Run fieldextra and save LOG file
    with open(output_dir / "LOG_ICON_ICON_REMAP.txt", "w") as f:
        _log_fx(f, remap_namelist_path)

    with open(output_dir / "LOG_ICON_ICON_REMAP.txt", "r") as f:
        _print_status(f, output_dir, file_out)

    return file_out


def _log_fx(f, remap_namelist_path):
    try:
        fieldextra_exe = os.environ["FIELDEXTRA_PATH"]
        fxcommand = f"ulimit -s unlimited;  export OMP_STACKSIZE=500M; {fieldextra_exe} {remap_namelist_path};"
        print("\nRunning fieldextra:" + f"{fieldextra_exe} {remap_namelist_path}")
        # Run fieldextra with namelist
        fx = subprocess.run(fxcommand, capture_output=True, check=True, shell=True)

        for line in fx.stdout.decode().split("\n"):
            f.write(line + "\n")
        for line in fx.stderr.decode().split("\n"):
            f.write(line + "\n")

    except subprocess.CalledProcessError as e:
        return_code = e.returncode
        raise Exception(
            "Error running fieldextra. CalledProcessError, Return Code: "
            + str(return_code)
        )


def _print_status(f, output_dir, file_out):
    for line in reversed(f.readlines()):
        line = line.rstrip()
        if len(line) > 1:
            lastline = line
            print("\n" + line)
            break
    if "successfully" in lastline.lower():
        print("Interpolated data stored at: " + str(file_out))
    if "exception" in lastline.lower():
        raise Exception(
            "Fieldextra did not run successfully, check the LOG: "
            + str(output_dir / "LOG_ICON_REG_REMAP.txt")
        )
