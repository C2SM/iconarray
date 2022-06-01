import xarray as xr
from .utilities import awhere_drop
from .latlonhash import icon2latlon
import numpy as np


class Crop:
    def __init__(self, grid: xr.Dataset, lon_bnds: list[float], lat_bnds: list[float]):
        self.full_grid = grid
        self.lon_bnds = lon_bnds
        self.lat_bnds = lat_bnds

    def reindex_neighbour_table(self, field, loc, target_grid):
        shape = field.shape
        lon_coord_name = loc[0] + "lon"
        lat_coord_name = loc[0] + "lat"

        neighbor_cell_index = field.data.flatten()
        lon_coords = self.full_grid.coords[lon_coord_name][neighbor_cell_index]
        lat_coords = self.full_grid.coords[lat_coord_name][neighbor_cell_index]
        i2ll = icon2latlon(target_grid)

        iind_lon, iind_lat = i2ll.latlon_indices_of_coords(loc, lon_coords, lat_coords)
        # if there is no neighbour, i.e index -1 or 0, the index was extracted
        # for value -1, which is a valid element index. Here we reset again the index
        # to -1
        iind_lon = iind_lon.where(neighbor_cell_index > 0, -1)
        iind_lat = iind_lat.where(neighbor_cell_index > 0, -1)

        cropped_clatlon_to_icon = i2ll.latlon_grid(loc)
        res = cropped_clatlon_to_icon[iind_lon, iind_lat].where(
            (iind_lon >= 0) & (iind_lat >= 0), -1
        )
        assert (np.amax(res.data) == len(target_grid.coords[lon_coord_name])) & (
            np.amin(res.data) >= -1
        )

        return xr.DataArray(
            data=res.data.reshape(shape), dims=field.dims, coords=field.coords
        )

    def reindex_neighbour_tables(self, target_grid):
        fieldloc = {
            "edge_of_cell": "edge",
            "vertex_of_cell": "vertex",
            "adjacent_cell_of_edge": "cell",
            "edge_vertices": "vertex",
            "cells_of_vertex": "cell",
            "edges_of_vertex": "edge",
            "vertices_of_vertex": "vertex",
            "neighbor_cell_index": "cell",
        }

        res_grid = target_grid.copy()

        for field in fieldloc:
            res_grid[field] = self.reindex_neighbour_table(
                target_grid[field], fieldloc[field], target_grid
            )

        return res_grid

    def crop_grid(self):
        return self.reindex_neighbour_tables(self.crop_fields())

    def crop_fields(self):

        filtered_grid = []
        for loc in ["cell", "edge", "vertex"]:
            loc_vars = [
                var
                for var in self.full_grid.data_vars
                if loc in self.full_grid[var].dims
            ]
            lon_coord_name = loc[0] + "lon"
            lat_coord_name = loc[0] + "lat"
            locgrid_filt = awhere_drop(
                self.full_grid[loc_vars],
                (self.full_grid.coords[lon_coord_name] > self.lon_bnds[0])
                & (self.full_grid.coords[lon_coord_name] < self.lon_bnds[1])
                & (self.full_grid.coords[lat_coord_name] > self.lat_bnds[0])
                & (self.full_grid.coords[lat_coord_name] < self.lat_bnds[1]),
            )
            filtered_grid.append(locgrid_filt)

        return xr.merge(filtered_grid)

    def crop_data(self, ds):

        ds_res = ds.copy()
        for coord in ["cell", "edge"]:
            if coord in ds.coords:
                lon_coord_name = coord[0] + "lon"
                lat_coord_name = coord[0] + "lat"
                ds_res = ds_res.where(
                    (self.full_grid.coords[lon_coord_name] > self.lon_bnds[0])
                    & (self.full_grid.coords[lon_coord_name] < self.lon_bnds[1])
                    & (self.full_grid.coords[lat_coord_name] > self.lat_bnds[0])
                    & (self.full_grid.coords[lat_coord_name] < self.lat_bnds[1]),
                    drop=True,
                )

        return ds_res
