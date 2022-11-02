.. iconarray documentation master file, created by
   sphinx-quickstart on Wed Jun  1 12:05:24 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started
=====================================



Iconarray and the packages it depends on are installable with conda. Some of these dependencies, 
eg eccodes and cartopy are not easily installable with pip, but easily installable with conda. 
If you are using iconarray in your own conda environment, you should add the packages in 
env/environment.yml to your environment.

Create a conda environment (eg. called iconarray) and install requirements:


.. code::

   conda env create -n iconarray -f env/environment.yml

Activate environment:

.. code::

   conda activate iconarray


ICON GRIB Definitions
----------------------------
If you are using the conda setup and want to use GRIB data, you will need to set the ```GRIB_DEFINITION_PATH```. This can be done on Tsa/Daint (CSCS) by sourcing the script setup-conda-env.sh. It only needs to be run a single time, as it will save the ```GRIB_DEFINITION_PATH``` environment variable to the conda environment. You will need to deactivate and reactivate the conda environment after doing this. You can check it has been correctly set by `conda env config vars list`. This script also sets the Fieldextra path, which is used for data interpolation.

.. code::

   source env/setup-conda-env.sh
