.. iconarray documentation master file, created by
   sphinx-quickstart on Wed Jun  1 12:05:24 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to iconarray's documentation!
=====================================

The iconarray python package contains various modules to facilitate working with ICON data with xarray 
or other xarray based tools (such as `psyplot <https://psyplot.github.io/>`__ - a plotting package). 
iconarray was developed together with  `icon-vis <https://github.com/C2SM/icon-vis>`__.

.. toctree::
   :glob:
   :hidden:
   :maxdepth: 1

   gettingstarted




.. grid:: 1
    :margin: 5 5 0 0
    :gutter: 0

    .. grid-item-card:: Getting started
      :columns: 6
      :link: gettingstarted
      :link-type: doc

      New to *iconarray*? Check out the getting started guide. This instructs you 
      how to create your conda environment, and using iconarray at CSCS.

API reference
==========================


This page provides an auto-generated summary of iconarray's API.

Core functions
------------------

.. currentmodule:: iconarray.core

.. autosummary::
   :toctree: generated/
   :caption: Core

   crop
   crop.Crop
   latlonhash
   latlonhash.Icon2latlon
   utilities
   utilities.ind_from_latlon
   utilities.show_data_vars
   interpolate
   interpolate.remap_ICON_to_regulargrid
   interpolate.remap_ICON_to_ICON


Backend functions
------------------

.. currentmodule:: iconarray.backend

.. autosummary::
   :toctree: generated/
   :caption: Backend

   grid
   grid.combine_grid_information
   grid.get_cell_dim_name
   grid.get_edge_dim_name
   grid.get_time_coord_name
   grid.add_cell_data
   grid.add_edge_data
   grid.open_dataset

Plotting functions
------------------

.. currentmodule:: iconarray.plot

.. autosummary::
   :toctree: generated/
   :caption: Plotting

   formatoptions
   formatoptions.borders
   formatoptions.lakes
   formatoptions.rivers
   config

Utility functions
------------------

.. currentmodule:: iconarray.utils

.. autosummary::
   :toctree: generated/
   :caption: Utility

   get_data
   get_data.get_example_data

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
