"""Functionality to locate ICON grid indices associated to lat/lon grid coordinates via hashing the indices in a Cartesian grid."""
import math
from typing import Tuple

import numpy as np
import xarray as xr


def _check_loc(loc):
    if loc not in ["cell", "edge", "vertex"]:
        raise ValueError("Wrong location: {loc}".format(loc=loc))


class _latlon_spec:
    def __init__(self, loc, lon_coords, lat_coords):
        self.lon_bnds = [np.amin(lon_coords).data, np.amax(lon_coords).data]
        self.lat_bnds = [np.amin(lat_coords).data, np.amax(lat_coords).data]
        self.Dlon = self.lon_bnds[1] - self.lon_bnds[0]
        self.Dlat = self.lat_bnds[1] - self.lat_bnds[0]
        self.cell_area = self.Dlon * self.Dlat / len(lon_coords) * 0.3
        self.ratio = self.Dlon / self.Dlat
        self.dlon = math.sqrt(self.cell_area)
        self.dlat = math.sqrt(self.cell_area)


class Icon2latlon:
    """Creates a field in a Cartesian lat/lon grid whose elements contain the ICON grid indices of the element whose lat/lon coordinates are contained within the cartesian element.

    It can be used as a hashing of the ICON grid indices in order to search for nearest neighbor ICON indices
    with O(1) complexity.

    Parameters
    ----------
    grid: xr.Dataset
        the ICON grid information, it should contain the following coordinates: clon,clat,elon,elat,vlon,vlat

    Example
    -------

    open the ICON grid:

    >>> ds_grid = xr.open_dataset("icon_grid_0001_R19B08_lon:0.1525-0.1535_lat:0.8748-0.8752.nc")

    create the 2D array that maps ICON grid indices into a lat/lon Cartesian grid

    >>> i2ll = Icon2latlon(ds_grid)
    >>> cartgrid_ind = i2ll.latlon_grid("cell")
    >>> cartgrid_ind
    ... array([[ 3,  0,  0,  1],
    ...     [ 0,  0,  0,  0],
    ...     [ 0,  4,  2,  0],
    ...     [ 0,  0,  0,  0],
    ...     [ 5,  0,  0,  9],
    ...     [ 0,  0,  0,  0],
    ...     [ 6,  0,  8,  0],
    ...     [ 0,  0,  0,  0],
    ...     [10,  0,  0,  0],
    ...     [ 0,  0,  0,  7]])
    ... Dimensions without coordinates: x, y

    the lat/lon bounds of the grid are lon:[0.1525,0.1535], lat[0.8748,0.8752]

    we can search for the ICON indices of the following coordinates:

    >>> lons = xr.DataArray([0.152871, 0.153016])
    >>> lats = xr.DataArray([0.875108, 0.874878])
    >>> inds_lon, inds_lat = i2ll.latlon_indices_of_coords("cell", lons, lats)
    >>> inds_lon
    ... <xarray.DataArray (cindex: 2)>
    ... array([2, 4])
    ... Dimensions without coordinates: cindex
    >>> inds_lat
    ...  <xarray.DataArray (cindex: 2)>
    ... array([2, 0])
    ... Dimensions without coordinates: cindex

    retrieve the ICON indices:

    >>> icon_inds = cartgrid_ind[inds_lon, inds_lat]
    >>> icon_inds
    ... <xarray.DataArray (cindex: 2)>
    ... array([2, 5])
    ... Dimensions without coordinates: cindex
    """

    def __init__(self, grid: xr.Dataset):
        self.grid = grid
        self.grid_spec = {}

        for loc in ["cell", "edge", "vertex"]:
            lon_coords_name = loc[0] + "lon"
            lat_coords_name = loc[0] + "lat"
            self.grid_spec[loc] = _latlon_spec(
                loc,
                self.grid.coords[lon_coords_name],
                self.grid.coords[lat_coords_name],
            )

    def latlon_indices_of_coords(
        self, loc: str, lons: xr.DataArray, lats: xr.DataArray
    ) -> Tuple[xr.DataArray, xr.DataArray]:
        """Retrieve the indices in the lat/lon grid associated with a sequence of lon/lat coordinates.

        Parameters
        ----------
        loc : str
            the location of the elements: cell, edge or vertex
        lons : xr.DataArray
            sequence of longitude coordinates
        lats : xr.DataArray
            sequence of latitude coordinates

        Returns
        -------
        indices : Tuple[xr.DataArray, xr.DataArray]
            indices for the Cartesian lat/lon grid pointing to the element with coordinates of the parameters lons/lats.
        """
        _check_loc(loc)
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

    def latlon_grid(self, loc) -> xr.DataArray:
        """Generate a lat/lon grid that covers the entire ICON grid.

        Each ICON grid element (cell, edge or vertex) falls only into one lat/lon grid cell.
        Some of the lat/lon grid cells might not contain any ICON grid element.

        Parameters
        ----------
        loc: the location of the elements that will be mapped into the lat/lon grid.
             Values must be one of ['cell','edge','vertex']
        Returns
        -------
        latlongrid: xarray.DataArray
            A new DataArray with x,y dimensions and lat/lon coordinates covering
            the original ICON grid. The values contain the indices of the corresponding
            element in the ICON grid.
        """
        _check_loc(loc)
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
