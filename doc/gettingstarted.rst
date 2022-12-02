.. iconarray documentation master file, created by
   sphinx-quickstart on Wed Jun  1 12:05:24 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started
=====================================


Iconarray and the packages it depends on are installable with conda. Some of these dependencies,
eg eccodes and cartopy are not easily installable with pip, but easily installable with conda.

First clone the iconarray repository and ``cd`` into its parent directory:

.. code::

   git clone git@github.com:C2SM/iconarray.git
   cd iconarray

If you are setting up a **new conda environment** for iconarray, carry out these two steps:

1. Create a conda environment (e.g. called iconarray) and install iconarray and its requirements:

   .. code::

      conda env create -n iconarray -f env/environment.yml

2. Activate environment:

   .. code::

      conda activate iconarray


Alternatively if you are adding iconarray to your **existing conda environment**,
carry out these two steps:

1. Update your existing conda environment by executing this command.
2. It will install iconarray and all its missing dependencies into your existing conda environment:

   .. code::

      conda env update -n {YOUR_ENVIRONMENT} -f env/environment.yml

3. You can then re-export an updated ``environment.yml`` file of your environment:

   .. code::

      conda activate {YOUR_ENVIRONMENT}
      conda env export | grep -v "^prefix: " > environment.yml

Alternatively, you can also update your own environment.yml file manually, according to the
``env/environment.yml`` file.


ICON GRIB Definitions
----------------------------
If you are using the conda setup and want to use GRIB data,
you probably need to set the ```GRIB_DEFINITION_PATH```.
The GRIB_DEFINITION_PATH environment variable can
be configured in order to use local definition files (text files defining the decoding rules)
instead of the default definition files provided with eccodes.
This can be done on Tsa/Daint (CSCS) by sourcing the script setup-conda-env.sh.
It only needs to be run a single time, as it will save the
```GRIB_DEFINITION_PATH``` environment variable to the conda environment.
You will need to deactivate and reactivate the conda environment after doing this.
You can check it has been correctly set by `conda env config vars list`.

.. code::

   ./env/setup-conda-env.sh

The above script also sets the Fieldextra installation path (```FIELDEXTRA_PATH```).
Fieldextra is a tool which can be used for interpolating data to another grid
(lon/lat or another ICON grid).
The use of this specific installation of Fieldextra depends on your CSCS access rights,
so you may need to change ```FIELDEXTRA_PATH``` if you have problems interpolating.
