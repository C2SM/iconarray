import xarray as xr
from utilities import awhere_drop
from latlonhash import icon2latlon
import numpy as np


class Crop:
    def __init__(self, grid: xr.Dataset, lon_bnds: list[float], lat_bnds: list[float]):
        self.full_grid = grid
        self.lon_bnds = lon_bnds
        self.lat_bnds = lat_bnds

    def crop_neighbour_table_index(self, field, target_grid):
        shape = field.shape
        loc = field.dims[-1]
        assert loc in ["cell", "edge", "vertex"]
        if loc == "cell":
            lon_coord_name = "clon"
            lat_coord_name = "clat"
        elif loc == "edge":
            lon_coord_name = "elon"
            lat_coord_name = "elat"
        elif loc == "vertex":
            lon_coord_name = "vlon"
            lat_coord_name = "vlat"
        else:
            raise ValueError("Wrong location for field")

        neighbor_cell_index = field.data.flatten()
        print("ooo", field.coords, field.dims)
        lon_coords = self.full_grid.coords[lon_coord_name][neighbor_cell_index]
        lat_coords = self.full_grid.coords[lat_coord_name][neighbor_cell_index]
        i2ll = icon2latlon(target_grid)
        iind_clon, iind_clat = i2ll.latlon_indices_of_coords(
            loc, lon_coords, lat_coords
        )
        print("RRR", lon_coords[0:100])
        iind_clon = iind_clon.where(neighbor_cell_index > 0, -1)
        iind_clat = iind_clat.where(neighbor_cell_index > 0, -1)

        print("LLL", iind_clon)
        print("jjj", np.amax(iind_clon), np.amax(iind_clat))

        cropped_clatlon_to_icon = i2ll.latlon_grid(loc)

        res = cropped_clatlon_to_icon[iind_clon, iind_clat].where(
            (iind_clon >= 0) & (iind_clat >= 0), -1
        )
        print("LLLLLL", res)
        assert (
            np.amax(res) == len(target_grid.coords[lon_coord_name]) & np.amin(res) > 0
        )

        return res

    def crop_grid(self):
        cell_vars = [
            var
            for var in self.full_grid.data_vars
            if "cell" in self.full_grid[var].dims
        ]
        cgrid_filt = awhere_drop(
            self.full_grid[cell_vars],
            (self.full_grid.coords["clon"] > self.lon_bnds[0])
            & (self.full_grid.coords["clon"] < self.lon_bnds[1])
            & (self.full_grid.coords["clat"] > self.lat_bnds[0])
            & (self.full_grid.coords["clat"] < self.lat_bnds[1]),
        )
        edge_vars = [
            var
            for var in self.full_grid.data_vars
            if "edge" in self.full_grid[var].dims
        ]

        egrid_filt = awhere_drop(
            self.full_grid[edge_vars],
            (self.full_grid.coords["elon"] > self.lon_bnds[0])
            & (self.full_grid.coords["elon"] < self.lon_bnds[1])
            & (self.full_grid.coords["elat"] > self.lat_bnds[0])
            & (self.full_grid.coords["elat"] < self.lat_bnds[1]),
        )

        vertex_vars = [
            var
            for var in self.full_grid.data_vars
            if "vertex" in self.full_grid[var].dims
        ]

        vgrid_filt = awhere_drop(
            self.full_grid[vertex_vars],
            (self.full_grid.coords["vlon"] > self.lon_bnds[0])
            & (self.full_grid.coords["vlon"] < self.lon_bnds[1])
            & (self.full_grid.coords["vlat"] > self.lat_bnds[0])
            & (self.full_grid.coords["vlat"] < self.lat_bnds[1]),
        )

        return xr.merge([cgrid_filt, egrid_filt, vgrid_filt])

    def __call__(self, grid: xr.Dataset):
        pass
