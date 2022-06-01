import xarray as xr
import numpy as np
import math


def check_loc(loc):
    if loc not in ["cell", "edge", "vertex"]:
        raise ValueError("Wrong location: {loc}".format(loc=loc))


class latlon_spec:
    def __init__(self, loc, lon_coords, lat_coords):
        self.lon_bnds = [np.amin(lon_coords).data, np.amax(lon_coords).data]
        self.lat_bnds = [np.amin(lat_coords).data, np.amax(lat_coords).data]
        self.Dlon = self.lon_bnds[1] - self.lon_bnds[0]
        self.Dlat = self.lat_bnds[1] - self.lat_bnds[0]
        self.cell_area = self.Dlon * self.Dlat / len(lon_coords) * 0.3
        self.ratio = self.Dlon / self.Dlat
        self.dlon = math.sqrt(self.cell_area)
        self.dlat = math.sqrt(self.cell_area)


class icon2latlon:
    def __init__(self, grid: xr.Dataset):
        # TODO Only coords are required
        self.grid = grid
        self.grid_spec = {}

        for loc in ["cell", "edge", "vertex"]:
            lon_coords_name = loc[0] + "lon"
            lat_coords_name = loc[0] + "lat"
            self.grid_spec[loc] = latlon_spec(
                loc,
                self.grid.coords[lon_coords_name],
                self.grid.coords[lat_coords_name],
            )

    def latlon_indices_of_coords(self, loc, lons, lats):
        check_loc(loc)
        iind_clon = xr.DataArray(
            (
                (lons.data - self.grid_spec[loc].lon_bnds[0]) / self.grid_spec[loc].dlon
            ).astype("int"),
            dims=[loc[0] + "index"],
        )
        iind_clon = iind_clon.where(
            (lons.data >= self.grid_spec[loc].lon_bnds[0])
            & (lons.data <= self.grid_spec[loc].lon_bnds[1]),
            -1,
        )
        iind_clat = xr.DataArray(
            (
                (lats.data - self.grid_spec[loc].lat_bnds[0]) / self.grid_spec[loc].dlat
            ).astype("int"),
            dims=[loc[0] + "index"],
        )
        iind_clat = iind_clat.where(
            (lats.data >= self.grid_spec[loc].lat_bnds[0])
            & (lats.data <= self.grid_spec[loc].lat_bnds[1]),
            -1,
        )

        return iind_clon, iind_clat

    def latlon_grid(self, loc):
        check_loc(loc)
        lon_coord_name = loc[0] + "lon"
        lat_coord_name = loc[0] + "lat"

        nx = int(
            (self.grid_spec[loc].Dlon + self.grid_spec[loc].dlon)
            / self.grid_spec[loc].dlon
        )
        ny = int(
            (self.grid_spec[loc].Dlat + self.grid_spec[loc].dlat)
            / self.grid_spec[loc].dlat
        )

        ind_clon, ind_clat = self.latlon_indices_of_coords(
            loc, self.grid.coords[lon_coord_name], self.grid.coords[lat_coord_name]
        )

        clatlon = xr.DataArray(data=np.zeros([nx, ny]).astype("int"), dims=["x", "y"])

        # Check indices are unique, i.e. only 1 ICON cell may fall into each lat/lon cell
        # We could do this with np.unique, but since it involves a sort (NlogN) this might be faster
        data_check = clatlon.copy()
        data_check[ind_clon, ind_clat] = -1
        assert np.count_nonzero(data_check == -1) == len(ind_clon)

        clatlon[ind_clon, ind_clat] = np.arange(len(ind_clon)) + 1
        return clatlon
