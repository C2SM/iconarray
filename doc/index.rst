.. iconarray documentation master file, created by
   sphinx-quickstart on Wed Jun  1 12:05:24 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to iconarray's documentation!
=====================================

The iconarray python package contains various modules to facilitate working with ICON data with xarray or other xarray based tools (such as psyplot - a plotting package). iconarray was developed together with icon-vis.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

API reference
=============

This page provides an auto-generated summary of iconarray's API.

Core functions
------------------

.. currentmodule:: iconarray.core

.. autosummary::
   :toctree: generated/

   crop
   crop.Crop
   latlonhash
   latlonhash.Icon2latlon
   utilities
   utilities.ind_from_latlon
   data_explorer.inspect_data
   data_explorer.show_data_vars
   interpolate
   interpolate.remap_ICON_to_regulargrid
   interpolate.remap_ICON_to_ICON


Backend functions
------------------

.. currentmodule:: iconarray.backend

.. autosummary::
   :toctree: generated/

   grid
   grid.combine_grid_information
   grid.get_cell_dim_name
   grid.get_edge_dim_name
   grid.get_time_coord_name
   grid.add_cell_data
   grid.add_edge_data
   grid.open_dataset
   grid.select_data

Plotting functions
------------------

.. currentmodule:: iconarray.plot

.. autosummary::
   :toctree: generated/

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

   get_data
   get_data.get_example_data

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
