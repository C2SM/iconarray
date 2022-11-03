# iconarray

[![Available on pypi](https://badge.fury.io/py/iconarray.svg)](https://pypi.python.org/pypi/iconarray/)
[![Docs](https://github.com/C2SM/iconarray/workflows/docs/badge.svg?branch=main)](https://c2sm.github.io/iconarray/)
[![Build Status](https://jenkins-mch.cscs.ch/job/iconarray_testsuite/badge/icon?config=build)](https://jenkins-mch.cscs.ch/job/iconarray_testsuite/)
[![Test Status](https://jenkins-mch.cscs.ch/job/iconarray_testsuite/badge/icon?config=test)](https://jenkins-mch.cscs.ch/job/iconarray_testsuite/)

## Introduction

The iconarray python package contains various modules to facilitate working with ICON data with xarray or other xarray based tools (such as psyplot - a plotting package). iconarray was developed together with [icon-vis](https://github.com/C2SM/icon-vis).

**API Documentation**: https://c2sm.github.io/iconarray/

# Table of contents
1. [Introduction](#introduction)
2. [Modules](#modules)
3. [Formatoptions](#formatoptions)
6. [Contacts](#contacts)
7. [Acknowledgments](#acknowledgments)

### Modules

There are a number of [modules](/iconarray) which are part of the `iconarray` package (installed by conda (see [env/environment.yml](env/environment.yml)), which you can import like a normal python package into your scripts. To work with the modules from iconarray, you can add this code block to the start of your script / notebook. You will see many examples of the modules being used within the scripts in this repo.

```python
import iconarray # import iconarray modules
from iconarray.plot import formatoptions # import plotting formatoptions (for use with psyplot)
```

Then you can use the functions or modules as needed, eg:

```python
iconarray.get_example_data()
```

#### grid - [modules/grid.py](modules/grid.py)

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

#### utils - [modules/utils.py](modules/utils.py)

**`ind_from_latlon()`** Returns the nearest neighbouring index of lat-lon within given lats-lons.

**`add_coordinates()`** Returns the position of given coordinates on the plot (useful to add markers at a fixed location).

**`get_stats()`** Returns the mean of two given variables, the difference of the mean and the p values.

**`wilks()`** Returns a value for which differences are significant when data point dependencies are accounted for (based on [Wilks 2016](https://journals.ametsoc.org/view/journals/bams/97/12/bams-d-15-00267.1.xml)).

**`show_data_vars()`** Returns a table with variables in your data. The first column shows the variable name psyplot will need to plot that variable.
This is useful if you plot GRIB data, because if `GRIB_cfVarName` is defined, cfgrib will set this as the variable name, as opposed to `GRIB_shortName` which you might expect.

#### interpolate.py - [modules/interpolate.py](modules/interpolate.py)

The functions in interpolate.py are used to facilitate the interpolation of ICON vector data to a regular grid, or a coarser ICON grid, for the purpose of vectorplots, eg wind plots. For psyplot we recommend to plot wind data on the regular grid as you can then scale the density of arrows in a vector plot as desired.

**`remap_ICON_to_ICON()`** This calls the `_create_remap_nl()` function to create a fieldextra namelist with your datafile, and subsequently runs fieldextra with this namelist. The output file along with a LOG and the namelist are saved in a `tmp` folder. The function returns the file location of the output file.

**`remap_ICON_to_regulargrid()`** This calls the `_create_remap_nl()` function to create a fieldextra namelist with your datafile, and subsequently runs fieldextra with this namelist. The output file along with a LOG and the namelist are saved in a `tmp` folder. The function returns the file location of the output file.

<hr>

Descriptions of the formatoption modules and data modules can be found in [Example Data](#example-data) and [Formatoptions](#formatoptions) sections.

### Formatoptions

Psyplot has a large number of ‘formatoptions’ which can be used to customize the look of visualizations. For example, the descriptions of the formatoptions associated with the MapPlotter class of psyplot can be found in the [psyplot documentation](https://psyplot.github.io/psy-maps/api/psy_maps.plotters.html#psy_maps.plotters.MapPlotter). The documentation for using formatoptions is also all on the psyplot documentation, or seen in the [examples](https://psyplot.github.io/examples/index.html).

Psyplot is designed in a way that is very modular and extensible, allowing users to easily create custom formatoptions and register them to plotters. Instructions for doing so are [here](https://psyplot.github.io/examples/general/example_extending_psyplot.html#3.-The-formatoption-approach).

This repository includes various custom formatoptions, that are not included in psyplot. For example:

* [Borders](/modules/formatoptions/borders.py) - Adds internal land borders to mapplot, vectorplots, and combinedplots.
* [Rivers](/modules/formatoptions/rivers.py) - Adds rivers to mapplot, vectorplots, and combinedplots.
* [Lakes](/modules/formatoptions/lakes.py) - Adds lakes to mapplot, vectorplots, and combinedplots.
* [Standard Title](/modules/formatoptions/standardtitle.py) - Adds a descriptive title based on your data to your mapplot.
* [Mean Max Wind](/modules/formatoptions/meanmaxwind.py) - Work In Progress.
* [Custom Text](/modules/formatoptions/customtext.py) - Work In Progress.

We encourage you to create your own formatoptions and contribute to this repository if they would be useful for others.

Once registered to a plotter class, the formatoptions can be used as seen in many of the scripts, for example in [mapplot.py](/mapplot/mapplot.py)
# Contacts

This repo has been developed by:
* Annika Lauber (C2SM) - annika.lauber@c2sm.ethz.ch
* Victoria Cherkas (MeteoSwiss) - victoria.cherkas@meteoswiss.ch
