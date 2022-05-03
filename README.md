# icon-vis

[![Build Status](https://jenkins-mch.cscs.ch/job/iconvis_utils_testsuite/badge/icon?config=build)](https://jenkins-mch.cscs.ch/job/iconvis_utils_testsuite/)
[![Build Status](https://jenkins-mch.cscs.ch/job/iconvis_utils_testsuite/badge/icon?config=test)](https://jenkins-mch.cscs.ch/job/iconvis_utils_testsuite/)

## Introduction
Collection of python scripts to visualise ICON-simulations on the unstructered grid. The different folders contain example code for different kind of plots. Example datasets for testing can be downloaded following the instructions in the [data](https://github.com/C2SM/icon-vis/tree/master/data) folder. Example plots for each folder are shown below. More detailed descriptions for each plot are in the README files of the different folders. The routines are mainly based on the python library  [psyplot](https://psyplot.github.io).
For visualizing data along a transect, [psy-transect](https://github.com/psyplot/psy-transect) is currently under development.

If you have any feature requests, feel free to raise an issue or contact us by email. We are also happy if you want so share your own plotting scripts.

# Table of contents
1. [Introduction](#introduction)
2. [Environment Setup](#environment-setup)
    - [Conda environment](#conda-environment)
3. [Usage](#usage)
    - [Modules](#modules)
    - [Formatoptions](#formatoptions)
4. [Example Plots](#example-plots)
6. [Contacts](#contacts)
7. [Acknowledgments](#acknowledgments)


# Getting started with psyplot
## Environment Setup
### Conda environment

<details>
  <summary>Installing Miniconda on Tsa/Daint (CSCS)</summary>

  ### Installing Miniconda on Tsa/Daint (CSCS)
1. Look up most recent Miniconda version for Linux 64-bit on the [Miniconda documentation pages](https://docs.conda.io/en/latest/miniconda.html)
2. Install as user specific miniconda e.g. on /scratch (enter ```cd $SCRATCH``` at the command line to get to your personal scratch directory).
   When the command prompt asks for installation location, provide the path to your scratch and append ```/miniconda3```.

        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

        bash Miniconda3-latest-Linux-x86_64.sh

3. Export path to your conda installation (if using daint/euler/tsa: install miniconda on scratch to avoid memory issues).

        export PATH="$SCRATCH/miniconda3/bin:$PATH"

</details>

Create a conda environement _psyplot_ with python[version>=3.7,<3.10] (psy-view requirement) and install requirements:

    conda env create -n psyplot -f env/environment.yml

Activate environment (use "source activate" in case "conda activate" does not work):

    conda activate psyplot

If you already have the environment but want to update it:

    conda env update --file local.yml --prune

If you are using the conda setup and want to use GRIB data, you will need to set the ```GRIB_DEFINITION_PATH```. This can be done on Tsa/Daint by sourcing the script ```setup-conda-env.sh```. It only needs to be run a single time, as it will save the ```GRIB_DEFINITION_PATH``` environment variable to the conda environment. You will need to deactivate and reactivate the conda environment after doing this. You can check it has been correctly set by ``` conda env config vars list```. This script also sets the Fieldextra path, which is used for data interpolation. See [FAQs](#trouble-shooting) if you get an error running this.

    source env/setup-conda-env.sh
    
You can install psy-transect with (not officially released yet):

    python -m pip install git+https://github.com/psyplot/psy-transect

After creating the virtual environment and installing the requirements, the environment only needs to be activated for future usage. Make sure that the path is exported to ```~/miniconda3/bin```.
# Usage
### Modules

There are a number of [modules](/icon_vis/icon_vis/modules) which are part of the `icon-vis` package (installed by conda (see [env/environment.yml](env/environment.yml)) or pip (see [env/requirements.txt](env/requirements.txt)), which you can import like a normal python package into your scripts. To work with the modules and formatoptions from icon-vis, you can add this code block to the start of your script / notebook. You will see many examples of the modules being used within the scripts in this repo.

```python
from icon_vis import formatoptions # import icon-vis self-written formatoptions
import icon_vis.modules as iconvis # import icon-vis self-written modules
```

Then you can use the functions or modules as needed, eg:

```python
iconvis.get_example_data()
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

**`remap_ICON_to_ICON()`** This calls the `create_ICON_to_ICON_remap_namelist()` function to create a fieldextra namelist with your datafile, and subsequently runs fieldextra with this namelist. The output file along with a LOG and the namelist are saved in a `tmp` folder. The function returns the file location of the output file.

**`remap_ICON_to_regulargrid()`** This calls the `create_ICON_to_Regulargrid_remap_nl()` function to create a fieldextra namelist with your datafile, and subsequently runs fieldextra with this namelist. The output file along with a LOG and the namelist are saved in a `tmp` folder. The function returns the file location of the output file.

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

# Acknowledgments
Whenever using psyplot for a publication it should be cited https://psyplot.github.io/psyplot/#how-to-cite-psyplot.
