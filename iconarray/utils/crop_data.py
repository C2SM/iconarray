"""
This script/module contains the function crop_data which can be used to crop ICON GRIB/NETCDF files.

If using as a script, you can simply run: `python crop_data.py`.
"""
import os
import logging
import xarray as xr
import numpy as np
import earthkit.data
import eccodes

from iconarray import Crop
from iconarray.backend.grid import _identify_datatype, get_cell_dim_name, get_edge_dim_name
from pathlib import Path

def crop_data(data, grid=None, suffix='cropped', bounds=None, scale=None):
    """
    Crop ICON data and save output with suffix.

    If using icon-vis repository, the data is downloaded to a data folder under icon-vis root directory.

    Parameters
    ----------

    data : Str | os.Path
        Path to the GRIB or NETCDF file representing ICON model output.

    grid : Str | os.Path
        Path to the NETCDF file representing an ICON grid.

    bounds : Array[]
        1D array of length 4: [min longitude, max longitude, min latitude, max latitude] in degrees. Takes precedence over scale if both are provided.

    scale : int
        Integer to scale down by, between 0 and 1, use instead of bounds. Eg if scale=0.1, lon/lat delta will by reduced by 10%.

    suffix : Str
        Suffix to add to the original filename as output.
        
    
    Raises
    ----------
    Exception
        If ....

    """

    if bounds is None and scale is None:
        scale = 0.5
        logging.warning("No bounds or scale provided, using default.")
        logging.info(f"Scaling lat/lon by {scale} each.")
    elif bounds is not None and scale is not None:
        scale = None
        logging.warning("Ignoring scale")

    cwd = Path(os.getcwd()).resolve()

    if isinstance(data, str):
        data = Path(data)
    if not os.path.isfile(data):
        raise Exception(f"File {data} does not appear to exist on the file system. Please provide file which is readable.")
    datatype = _identify_datatype(data)
    if not datatype in ('grib','nc'):
        raise Exception('Please provide ICON data in either GRIB or NETCDF format.')
    output_file = cwd / (data.stem+'_'+suffix+data.suffix)
    # If output file already exist, delete it first.
    if os.path.isfile(output_file):
        logging.warning(f"Output file {output_file.name} already exists. Deleting {output_file.name}")
        os.remove(output_file)
    
    if grid is not None:
        if isinstance(grid, str):
            grid = Path(grid)
        if not os.path.isfile(grid):
            raise Exception(f"Grid file {grid} does not appear to exist on the file system. Please provide file which is readable.")
        if not _identify_datatype(grid) == 'nc':
            raise Exception('Grid file is not NETCDF.')
        output_grid = cwd / (grid.stem+'_'+suffix+grid.suffix)
        # If output grid already exist, delete it first.
        if os.path.isfile(output_grid):
            logging.warning(f"Output grid {output_grid.name} already exists. Deleting {output_grid.name}")
            os.remove(output_grid)

        grid_ds = xr.open_dataset(grid, engine='netcdf4')

        # Calculate bounds from scale
        if bounds is None and scale is not None:
            grid_bounds = np.min(grid_ds.clon.data),np.max(grid_ds.clon.data), np.min(grid_ds.clat.data),np.max(grid_ds.clat.data) 
            dlon = grid_bounds[1]-grid_bounds[0]
            dlat = grid_bounds[3]-grid_bounds[2]
            bounds = [grid_bounds[0] + dlon*scale/2, grid_bounds[1] - dlon*scale/2, grid_bounds[2] + dlat*scale/2, grid_bounds[3] - dlat*scale/2]
        
        logging.info(f"Original grid: lon {np.rad2deg(grid_bounds[0:2])} and lat {np.rad2deg(grid_bounds[2:])}")
        logging.info(f"Cropped grid:  lon {np.rad2deg(bounds[0:2])} and lat {np.rad2deg(bounds[2:])}")

        crop = Crop(grid_ds, bounds[0:2], bounds[2:], scale_factor=0.1)

        cropped_grid_ds = crop.cropped_grid()

        if datatype == 'grib':
            fs = earthkit.data.from_source("file", str(data))

            xarray_open_dataset_kwargs = {'backend_kwargs':{
                            "read_keys": ["typeOfLevel", "gridType"],
                        }, 'encode_cf':("time", "geography", "vertical")}
            
            with open(output_file, "wb") as outf:            
                for param in fs.indices()['param']:
                    fs_sel = fs.sel(param=param)
                    
                    try:
                        ds = fs_sel.to_xarray(xarray_open_dataset_kwargs=xarray_open_dataset_kwargs)
                    except AssertionError:
                        continue
                    if get_cell_dim_name(ds,grid_ds):
                        ds = ds.rename({str(get_cell_dim_name(ds,grid_ds)): "cell"})
                    elif get_edge_dim_name(ds,grid_ds):
                        ds = ds.rename({str(get_edge_dim_name(ds,grid_ds)): "edge"})
                    else:
                        raise Exception(f"Vertex not implemented yet, param {param}")


                    ds_cropped = crop(ds)

                    for rec in fs_sel:
                        level = rec['level']
                        if len(ds_cropped[param].coords[ds_cropped[param].attrs['GRIB_typeOfLevel']].values) > 1:
                            eccodes.codes_set_values(rec.handle._handle, ds_cropped[param].isel({rec["typeOfLevel"]:np.where(ds_cropped[param][rec["typeOfLevel"]].values==level)[0][0]-1}).squeeze().values)
                        else:
                            # Check if dataarray has any non NaN values, eccodes codes_set_values can't set only NaN
                            if any(np.isfinite(ds_cropped[param].squeeze().values)):
                                eccodes.codes_set_values(rec.handle._handle, ds_cropped[param].squeeze().values)
                            else:
                                logging.warning(f"Ignoring param {param} - only NaN values")
                        rec.write(outf)

        elif datatype == 'nc':
            ds = xr.open_dataset(data, engine='netcdf4')
            # ICON CF conventions require that the dimension is named any of (cell,edge,vertex), instead of values
            ds = ds.rename({str(get_cell_dim_name(ds,grid_ds)): "cell"})
            ds_cropped = crop(ds)

            ds_cropped.to_netcdf(output_file)

        # Save cropped grid as NETCDF from xarray.
        cropped_grid_ds.to_netcdf(output_grid)

    else:
        raise Exception('Implementation without grid provided is not implemented yet.')


    logging.info(f"Output will be saved to: {output_file} and {output_grid}")



    return output_file, output_grid



if __name__ == "__main__":
    # crop_data("/scratch/vcherkas/iconarray/data/example_data/nc/lfff01000000.nc"
    #           ,'/scratch/vcherkas/iconarray/data/example_data/grids/ICON-1E_DOM01.nc',"crop",scale=0.7)

    crop_data("/scratch/vcherkas/iconarray/data/example_data/grib/lfff00010000_edgeplots"
              ,'/scratch/vcherkas/iconarray/data/example_data/grids/icon_grid_0001_R19B08_mch.nc',"crop",scale=0.7)


# set(fs.metadata("typeOfLevel"))

# fs.sel(typeOfLevel='entireLake').metadata()[0]['vertical']

# {typeOfLevel:[fs.sel(typeOfLevel=typeOfLevel).metadata()[0]['vertical']] for typeOfLevel in set(fs.metadata("typeOfLevel"))}

# len(ds_cropped[param].coords[ds_cropped[param].attrs['GRIB_typeOfLevel']].values)