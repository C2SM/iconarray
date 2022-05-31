import xarray as xr
from crop import Crop

def test_crop():

    in_data='/code/rz+/icon_data_processing_incubator/data/ICON/R19B08/lfff00010000'
    in_grid='/code/rz+/icon_data_processing_incubator/data/ICON/R19B08/icon_grid_0001_R19B08_mch.nc'

    lon_range=[0.165, 0.18] 
    lat_range=[0.8, 0.81]

    ds_grid = xr.open_dataset(in_grid)

    crop = Crop(ds_grid, [0.165, 0.18],[0.8,0.81])
    grid_cropped = crop.crop_grid()

    #rdata=crop_data(in_data, ds_grid, lon_range, lat_range)


    crop.crop_neighbour_table_index(grid_cropped['neighbor_cell_index'], grid_cropped)
