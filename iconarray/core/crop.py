"""functionality to crop both ICON grids and datasets on any grid location."""
from typing import Dict, List

import numpy as np
import xarray as xr

from .latlonhash import Icon2latlon


class Crop:
    """Cut the domain of an ICON grid and data to a region specified by a lat/lon retangle.

    All cells whose center coordinates are not contained within the lat/lon region will be dropped.
    All neighbour edges and vertices of the selected cells will be included in the cropped domain.
    As a result, some edges and/or vertices, boundaries of an included triangle, might have coordinate
    that are not contained within the lat/lon region.

    Parameters
    ----------
    grid : xr.Dataset
        The input dataset representing an ICON grid. The dataset should contain at least:

        - cell,edge and vertex dimensions.
        - clon,clat,elon,elat,vlon,vlat coordinates
        - edge_of_cell, vertex_of_cell variables that provide the connectivity between edge and vertex locations to the cell

    Examples
    --------
    load the grid dataset:

    >>> in_grid = 'icon_grid_0001_R19B08.nc'
    >>> grid = xr.open_dataset(in_grid)
    >>> grid
    ... <xarray.Dataset>
    ... Dimensions:                        (cell: 1043968, vertex: 523485,
    ...                                     edge: 1567452, nv: 3, nc: 2, ne: 6, no: 4,
    ...                                     max_chdom: 1, cell_grf: 14, edge_grf: 24,
    ...                                     vert_grf: 13)
    ... Coordinates:
    ...     clon                           (cell) float64 0.2887 0.2889 ... 0.2423
    ...     clat                           (cell) float64 0.7384 0.7384 ... 0.7474
    ...     vlon                           (vertex) float64 ...
    ...     vlat                           (vertex) float64 ...
    ...     elon                           (edge) float64 ...
    ...     elat                           (edge) float64 ...
    ... Dimensions without coordinates: cell, vertex, edge, nv, nc, ne, no, max_chdom,
    ...                                 cell_grf, edge_grf, vert_grf
    ... Data variables: (12/51)
    ...     cartesian_x_vertices           (vertex) float64 ...
    ...     cartesian_y_vertices           (vertex) float64 ...
    ...     cartesian_z_vertices           (vertex) float64 ...
    ...     cell_area                      (cell) float64 ...
    ...     dual_area                      (vertex) float64 ...
    ...     lon_cell_centre                (cell) float64 ...
    ...     ...                             ...
    ...     end_idx_e                      (max_chdom, edge_grf) int32 ...
    ...     refin_v_ctrl                   (vertex) int32 ...
    ...     start_idx_v                    (max_chdom, vert_grf) int32 ...
    ...     end_idx_v                      (max_chdom, vert_grf) int32 ...
    ...     parent_edge_index              (edge) int32 ...
    ...     parent_vertex_index            (vertex) int32 ...
    ... Attributes: (12/18)
    ...     title:                ICON grid description
    ...     institution:          Max Planck Institute for Meteorology/Deutscher Wett...
    ...     source:               svn://rclh.dwd.de/for0adm/SVN_icontools/tags/iconto...
    ...     number_of_grid_used:  1
    ...     ICON_grid_file_uri:
    ...     centre:               215
    ...     ...                   ...
    ...     inverse_flattening:   0.0
    ...     grid_level:           8
    ...     grid_root:            19
    ...     uuidOfParHGrid:       e6ddd597-9c90-27b1-fbac-c40d47f72ba0
    ...     uuidOfHGrid:          5a0a863d-2523-9515-7789-4930e3452bc0
    ...     global_grid:          0

    create a crop instance with the lat/lon coordinates for the region of interest

    >>> crop = Crop(grid, [0.148, 0.155], [0.871, 0.877])
    >>> crop.cropped_grid()
    ... Dimensions:                         (cell: 986, nv: 3, edge: 1530, nc: 2, no: 4,
    ...                                     vertex: 545, ne: 6)
    ... Coordinates:
    ...     clon                           (cell) float64 0.1544 0.1546 ... 0.1549
    ...     clat                           (cell) float64 0.8766 0.8768 ... 0.871 0.8711
    ...     elon                           (edge) float64 ...
    ...     elat                           (edge) float64 ...
    ...     vlon                           (vertex) float64 ...
    ...     vlat                           (vertex) float64 ...
    ... Dimensions without coordinates: cell, nv, edge, nc, no, vertex, ne
    ... Data variables: (12/45)
    ...     cell_area                      (cell) float64 ...
    ...     lon_cell_centre                (cell) float64 ...
    ...     lat_cell_centre                (cell) float64 ...
    ...     edge_of_cell                   (nv, cell) int64 1 2 766 766 ... 1528 205 205
    ...     vertex_of_cell                 (nv, cell) int64 1 137 341 138 ... 245 244 9
    ...     cell_area_p                    (cell) float64 ...
    ...     ...                             ...
    ...     dual_area_p                    (vertex) float64 ...
    ...     vlon_vertices                  (vertex, ne) float64 ...
    ...     vlat_vertices                  (vertex, ne) float64 ...
    ...     edge_orientation               (ne, vertex) int32 ...
    ...     refin_v_ctrl                   (vertex) int32 ...
    ...     parent_vertex_index            (vertex) int32 ...
    ... Attributes: (12/18)
    ...     title:                ICON grid description
    ...     institution:          Max Planck Institute for Meteorology/Deutscher Wett...
    ...     source:               svn://rclh.dwd.de/for0adm/SVN_icontools/tags/iconto...
    ...     number_of_grid_used:  1
    ...     ICON_grid_file_uri:
    ...     centre:               215
    ...     ...                   ...
    ...     inverse_flattening:   0.0
    ...     grid_level:           8
    ...     grid_root:            19
    ...     uuidOfParHGrid:       e6ddd597-9c90-27b1-fbac-c40d47f72ba0
    ...     uuidOfHGrid:          5a0a863d-2523-9515-7789-4930e3452bc0
    ...     global_grid:          0

    open a dataset with data:

    >>> ds_cell = xr.open_dataset("lfff00010000_cell.nc")
    >>> ds_cell
    ... Dimensions:                  (generalVerticalLayer: 80, time: 1, cell: 1043968,
    ...                               vertices: 3)
    ... Coordinates:
    ...     number                   int64 1
    ...     forecast_reference_time  datetime64[ns] 2022-02-16
    ...     step                     timedelta64[ns] 01:00:00
    ...   * generalVerticalLayer     (generalVerticalLayer) float64 1.0 2.0 ... 80.0
    ...   * time                     (time) datetime64[ns] 2022-02-16T01:00:00
    ...     clon                     (cell) float32 0.2887 0.2889 ... 0.2422 0.2423
    ...     clat                     (cell) float32 0.7384 0.7384 ... 0.7472 0.7474
    ...     clat_bnds                (cell, vertices) float32 0.7385 0.7384 ... 0.7475
    ...     clon_bnds                (cell, vertices) float32 0.2888 0.2886 ... 0.2423
    ... Dimensions without coordinates: cell, vertices
    ... Data variables:
    ...     unknown                  (time, generalVerticalLayer, cell) float32 0.0 ....
    ...     pres                     (time, generalVerticalLayer, cell) float32 4.675...
    ...     t                        (time, generalVerticalLayer, cell) float32 213.0...
    ...     u                        (time, generalVerticalLayer, cell) float32 0.0 ....
    ...     v                        (time, generalVerticalLayer, cell) float32 -9.53...
    ...     q                        (time, generalVerticalLayer, cell) float32 3.067...
    ...     clwmr                    (time, generalVerticalLayer, cell) float32 0.0 ....
    ... Attributes:
    ...     GRIB_edition:            2
    ...     GRIB_centre:             lssw
    ...     GRIB_centreDescription:  Zurich
    ...     GRIB_subCentre:          255
    ...     Conventions:             CF-1.7
    ...     institution:             Zurich

    crop the dataset that contains all cell variables:

    >>> cell_rds = crop(ds_cell)
    >>> cell_rds
    ... Dimensions:                  (generalVerticalLayer: 80, time: 1, cell: 986,
    ...                             vertices: 3)
    ... Coordinates:
    ...     number                   int64 1
    ...     forecast_reference_time  datetime64[ns] 2022-02-16
    ...     step                     timedelta64[ns] 01:00:00
    ... * generalVerticalLayer     (generalVerticalLayer) float64 1.0 2.0 ... 80.0
    ... * time                     (time) datetime64[ns] 2022-02-16T01:00:00
    ...     clon                     (cell) float32 0.1544 0.1546 ... 0.1547 0.1549
    ...     clat                     (cell) float32 0.8766 0.8768 ... 0.871 0.8711
    ...     clat_bnds                (cell, vertices) float32 0.8765 0.8767 ... 0.8712
    ...     clon_bnds                (cell, vertices) float32 0.1544 0.1546 ... 0.1547
    ... Dimensions without coordinates: cell, vertices
    ... Data variables:
    ...     unknown                  (time, generalVerticalLayer, cell) float32 0.0 ....
    ...     pres                     (time, generalVerticalLayer, cell) float32 4.596...
    ...     t                        (time, generalVerticalLayer, cell) float32 213.2...
    ...     u                        (time, generalVerticalLayer, cell) float32 21.96...
    ...     v                        (time, generalVerticalLayer, cell) float32 -11.1...
    ...     q                        (time, generalVerticalLayer, cell) float32 3.034...
    ...     clwmr                    (time, generalVerticalLayer, cell) float32 0.0 ....
    ... Attributes:
    ...     GRIB_edition:            2
    ...     GRIB_centre:             lssw
    ...     GRIB_centreDescription:  Zurich
    ...     GRIB_subCentre:          255
    ...     Conventions:             CF-1.7
    ...     institution:             Zurich
    """

    def __init__(self, grid: xr.Dataset, lon_bnds: list[float], lat_bnds: list[float]):
        grid_lon_bnds = [
            np.amin(grid.coords["clon"].data),
            np.amax(grid.coords["clon"].data),
        ]
        grid_lat_bnds = [
            np.amin(grid.coords["clat"].data),
            np.amax(grid.coords["clat"].data),
        ]

        if (
            (lon_bnds[0] > grid_lon_bnds[1])
            | (lat_bnds[0] > grid_lat_bnds[1])
            | (lon_bnds[1] < grid_lon_bnds[0])
            | (lat_bnds[1] < grid_lat_bnds[0])
        ):
            raise ValueError(
                "region of interest not within the grid domain:",
                grid_lon_bnds,
                grid_lat_bnds,
            )

        self.full_grid = grid
        self.lon_bnds = lon_bnds
        self.lat_bnds = lat_bnds
        self.idx_subset: Dict[str, List[int]] = {}
        self.rgrid = self.crop_grid()

    def _reindex_neighbour_table(self, field, loc, target_grid):
        shape = field.shape
        lon_coord_name = loc[0] + "lon"
        lat_coord_name = loc[0] + "lat"

        neighbor_flat_index = field.data.flatten() - 1

        # the neighbor indices of a look up table might fall out of the domain of a given location,
        # as defined by the list of indices in self.idx_subset.
        # Those out of the domain are set to -1
        neighbor_flat_index = np.vectorize(
            lambda elem: elem if elem in self.idx_subset[loc] else -1
        )(neighbor_flat_index)

        # list of coordinates for the indices of the neighbors
        lon_coords = self.full_grid.coords[lon_coord_name][neighbor_flat_index]
        lat_coords = self.full_grid.coords[lat_coord_name][neighbor_flat_index]
        i2ll = Icon2latlon(target_grid)

        # compute the list of cartesian coordinates of a lat/lon grid where
        # the coordinates (of the lookup table elements) fall
        iind_lon, iind_lat = i2ll.latlon_indices_of_coords(loc, lon_coords, lat_coords)

        # if there is no neighbour, i.e index -1 , then a corresponding cartesian coordinate
        # was was extracted for value -1 (which is a valid python element index).
        # Here we reset again the cartesian coordinate index to -1
        iind_lon = iind_lon.where(neighbor_flat_index >= 0, -1)
        iind_lat = iind_lat.where(neighbor_flat_index >= 0, -1)

        # 2d array that contains the mapping from cartesian coordinate (lat/lon) to the ICON index
        cropped_clatlon_to_icon = i2ll.latlon_grid(loc)
        # We dereference the final ICON index given the known cartesian coordinates
        res = cropped_clatlon_to_icon[iind_lon, iind_lat].where(
            (iind_lon >= 0) & (iind_lat >= 0), -1
        )

        if np.amax(res.data) != len(target_grid.coords[lon_coord_name]):
            raise ValueError("wrong number of indices after crop operation")

        if np.any((res.data == 0) | (res.data < -1)):
            raise ValueError("indices must be positive (except special value -1)")

        return xr.DataArray(
            data=res.data.reshape(shape), dims=field.dims, coords=field.coords
        )

    def _reindex_neighbour_tables(self, target_grid):

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
            res_grid[field] = self._reindex_neighbour_table(
                target_grid[field], fieldloc[field], target_grid
            )

        return res_grid

    def crop_grid(self):
        """Crop the coordinates for cells, edges and vertices.

        All cell variables are cropped to be within the required lat/lon box.
        In order to always work with regions composed by closed triangles,
        all neighbor edges and vertices of the selected cells are included.

        All neighbor lookup tables are also cropped and the indices are remapped
        to the new indexing space for the different locations (cell, edge, vertex)

        Returns
        -------
        A new dataset with all grid variables cropped to the target domain
        """
        self.idx_subset["cell"] = np.argwhere(
            (self.full_grid.coords["clon"].data > self.lon_bnds[0])
            & (self.full_grid.coords["clon"].data < self.lon_bnds[1])
            & (self.full_grid.coords["clat"].data > self.lat_bnds[0])
            & (self.full_grid.coords["clat"].data < self.lat_bnds[1]),
        ).flatten()
        self.idx_subset["edge"] = np.unique(
            self.full_grid["edge_of_cell"][:, self.idx_subset["cell"]].data.flatten()
            - 1
        )
        self.idx_subset["vertex"] = np.unique(
            self.full_grid["vertex_of_cell"][:, self.idx_subset["cell"]].data.flatten()
            - 1
        )

        return self._reindex_neighbour_tables(self.crop_fields())

    def crop_fields(self):
        """Crop all variables of the grid.

        All cell variables are cropped to be within the required lat/lon box.
        In order to always work with regions composed by full triangles,
        all edges and vertices neighbor of the selected cells are included.
        Note that the indices of the neighbor lookup tables are not yet
        remapped to the new indexing space after fields are cropped (and therefore
        are not well defined after call to this function)

        See Also
        --------
        Crop._reindex_neighbour_tables

        Returns
        -------
        A new dataset with all the cropped variables.
        """
        filtered_grid = []
        for loc in ["cell", "edge", "vertex"]:
            loc_vars = [
                var
                for var in self.full_grid.data_vars
                if loc in self.full_grid[var].dims
            ]
            locgrid_filt = self.full_grid[loc_vars].loc[{loc: self.idx_subset[loc]}]
            filtered_grid.append(locgrid_filt)

        return xr.merge(filtered_grid)

    def cropped_grid(self):
        """Return a dataset of a grid cropped to the lat/lon area specified.

        Returns
        -------
        A (new) cropped dataset with the grid information
        """
        return self.rgrid

    def __call__(self, ds):
        """Perform the crop on a dataset.

        Parameters
        ----------
        ds: xr.Dataset
            the dataset to be cropped

        Returns
        -------
        a (new) cropped dataset
        """
        res = ds
        for loc in ["cell", "edge", "vertex"]:
            if loc in ds.dims:
                res = res.sel({loc: self.idx_subset[loc]})
        return res
