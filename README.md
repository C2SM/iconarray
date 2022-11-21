# iconarray

[![Available on pypi](https://badge.fury.io/py/iconarray.svg)](https://pypi.python.org/pypi/iconarray/)
[![Docs](https://github.com/C2SM/iconarray/workflows/docs/badge.svg?branch=main)](https://c2sm.github.io/iconarray/)
[![Build Status](https://jenkins-mch.cscs.ch/job/iconarray_testsuite/badge/icon?config=build)](https://jenkins-mch.cscs.ch/job/iconarray_testsuite/)
[![Test Status](https://jenkins-mch.cscs.ch/job/iconarray_testsuite/badge/icon?config=test)](https://jenkins-mch.cscs.ch/job/iconarray_testsuite/)

## Introduction

The iconarray python package contains various modules to facilitate working with ICON data with xarray or other xarray based tools (such as psyplot - a plotting package). The package was developed together with [icon-vis](https://github.com/C2SM/icon-vis).


**API Documentation**: https://c2sm.github.io/iconarray

# Table of contents

1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Modules](#modules)
4. [Formatoptions](#formatoptions)
5. [Contacts](#contacts)

## Installation and Setup

Iconarray and the packages it depends on are installable with conda. Some of these dependencies, e.g. eccodes and cartopy are not easily installable with pip, but easily installable with conda. If you are adding iconarray to your own/existing conda environment, you should add the packages to your environment as in [env/environment.yml](env/environment.yml).

Create a conda environment (e.g. called iconarray) and install requirements:
```
conda env create -n iconarray -f env/environment.yml
```
Activate environment:
```
conda activate iconarray
```
#### ICON GRIB Definitions:
If you are using the conda setup and want to use GRIB data, you probably need to set the `GRIB_DEFINITION_PATH`. The GRIB_DEFINITION_PATH environment variable can be configured in order to use local definition files (text files defining the decoding rules) instead of the default definition files provided with eccodes. This can be done on Tsa/Daint (CSCS) by sourcing the script setup-conda-env.sh. It only needs to be run a single time, as it will save the `GRIB_DEFINITION_PATH` environment variable to the conda environment. You will need to deactivate and reactivate the conda environment after doing this. You can check it has been correctly set by conda env config vars list.

```
source env/setup-conda-env.sh
```

The above script also sets the Fieldextra installation path (`FIELDEXTRA_PATH`). Fieldextra is a tool which can be used for interpolating data to another grid (lon/lat or another ICON grid). The use of this specific installation of Fieldextra depends on your CSCS access rights, so you may need to change `FIELDEXTRA_PATH` if you have problems interpolating.

## Modules

There are a number of [modules](/iconarray) which are part of the `iconarray` package (installed by conda using [env/environment.yml](env/environment.yml)), which you can import like a normal python package into your scripts. To work with the modules from iconarray, you can add this code block to the start of your script / notebook. You will see many examples of the modules being used within the scripts in this repo.

```python
import iconarray # import iconarray modules
from iconarray.plot import formatoptions # import plotting formatoptions (for use with psyplot)
```

Then you can use the functions or modules as needed, eg:

```python
iconarray.get_example_data()
```

#### Grid - [backend/grid.py](/iconarray/backend/grid.py)

**`combine_grid_information()`** This adds the required grid information from a provided grid file to your dataset if not present. It also adds coordinates encoding to each variable, which is needed to plot using psyplot.

**`check_grid_information()`** Checks whether or not the grid data needs to be added. eg:

```python
if check_grid_information(nc_file):
    print('The grid information is available')
    data = psy.open_dataset(nc_file)
else:
    print('The grid information is not available')
    data = combine_grid_information(nc_file,grid_file)
```

#### Utilities - [core/utilities.py](/iconarray/core/utilities.py)

**`ind_from_latlon()`** Returns the nearest neighbouring index of lat-lon within given lats-lons.

**`add_coordinates()`** Returns the position of given coordinates on the plot (useful to add markers at a fixed location).

**`get_stats()`** Returns the mean of two given variables, the difference of the mean and the p values.

**`wilks()`** Returns a value for which differences are significant when data point dependencies are accounted for (based on [Wilks 2016](https://journals.ametsoc.org/view/journals/bams/97/12/bams-d-15-00267.1.xml)).

**`show_data_vars()`** Returns a table with variables in your data. The first column shows the variable name psyplot will need to plot that variable.
This is useful if you plot GRIB data, because if `GRIB_cfVarName` is defined, cfgrib will set this as the variable name, as opposed to `GRIB_shortName` which you might expect.

#### Interpolate - [core/interpolate.py](/iconarray/core/interpolate.py)

The functions in interpolate.py are used to facilitate the interpolation of ICON vector data to a regular grid, or a coarser ICON grid, for the purpose of vectorplots, eg wind plots. For psyplot we recommend to plot wind data on the regular grid as you can then scale the density of arrows in a vector plot as desired.

**`remap_ICON_to_ICON()`** This calls the `_create_remap_nl()` function to create a fieldextra namelist with your datafile, and subsequently runs fieldextra with this namelist. The output file along with a LOG and the namelist are saved in a `tmp` folder. The function returns the file location of the output file.

**`remap_ICON_to_regulargrid()`** This calls the `_create_remap_nl()` function to create a fieldextra namelist with your datafile, and subsequently runs fieldextra with this namelist. The output file along with a LOG and the namelist are saved in a `tmp` folder. The function returns the file location of the output file.

## Formatoptions

Psyplot has a large number of ‘formatoptions’ which can be used to customize the look of visualizations. For example, the descriptions of the formatoptions associated with the MapPlotter class of psyplot can be found in the [psyplot documentation](https://psyplot.github.io/psy-maps/api/psy_maps.plotters.html#psy_maps.plotters.MapPlotter). The documentation for using formatoptions is also all on the psyplot documentation, or seen in the [examples](https://psyplot.github.io/examples/index.html).

Psyplot is designed in a way that is very modular and extensible, allowing users to easily create custom formatoptions and register them to plotters. Instructions for doing so are [here](https://psyplot.github.io/examples/general/example_extending_psyplot.html#3.-The-formatoption-approach).

This repository includes various custom formatoptions, that are not included in psyplot. For example:

* [Borders](/iconarray/plot/formatoptions/borders.py) - Adds internal land borders to mapplot, vectorplots, and combinedplots.
* [Rivers](/iconarray/plot/formatoptions/rivers.py) - Adds rivers to mapplot, vectorplots, and combinedplots.
* [Lakes](/iconarray/plot/formatoptions/lakes.py) - Adds lakes to mapplot, vectorplots, and combinedplots.
* [Standard Title](/iconarray/plot/formatoptions/standardtitle.py) - Adds a descriptive title based on your data to your mapplot.
* [Mean Max Wind](/iconarray/plot/formatoptions/meanmaxwind.py) - Work In Progress.
* [Custom Text](/iconarray/plot/formatoptions/customtext.py) - Work In Progress.

We encourage you to create your own formatoptions and contribute to this repository if they would be useful for others.

Once registered to a plotter class, the formatoptions can be used as seen in many of the icon-vis scripts, for example in [mapplot.py](https://github.com/C2SM/icon-vis/blob/master/mapplot/mapplot.py).

# Contacts

This repo has been developed by:
* Annika Lauber (C2SM) - annika.lauber@c2sm.ethz.ch
* Victoria Cherkas (MeteoSwiss) - victoria.cherkas@meteoswiss.ch
