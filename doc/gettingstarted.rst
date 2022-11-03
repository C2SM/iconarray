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

   source env/setup-conda-env.sh

The above script also sets the Fieldextra installation path (```FIELDEXTRA_PATH```).
Fieldextra is a tool which can be used for interpolating data to another grid 
(lon/lat or another ICON grid).
The use of this specific installation of Fieldextra depends on your CSCS access rights, 
so you may need to change ```FIELDEXTRA_PATH``` if you have problems interpolating.