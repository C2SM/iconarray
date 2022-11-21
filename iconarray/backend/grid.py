"""The grid module contains functions relating to the grid information for ICON data, such as merging ICON data with the grid data to provide one merged dataset."""

import codecs
import logging
import pathlib
import sys

import cfgrib
import numpy as np
import psyplot.project as psy
import six
import xarray as xr


class WrongGridException(Exception):
    """Indicate wrong grid provided to be merged with ICON data."""

    def __init__(
        self,
        grid,
        message="""It looks like this grid you are trying to merge could be wrong. There are no dimensions in the data with {cells} cells or {edges} edges. """,
    ):
        self.grid = grid
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message.format(
            cells=self.grid.dims["cell"], edges=self.grid.dims["edge"]
        )


def _add_cell_encoding(obj):
    try:
        if "clat" not in obj.encoding["coordinates"]:
            obj.encoding["coordinates"] += " clat"
        if "clon" not in obj.encoding["coordinates"]:
            obj.encoding["coordinates"] += " clon"
    except Exception:
        obj.encoding["coordinates"] = "clon clat"


def _add_edge_encoding(obj):
    try:
        if "elat" not in obj.encoding["coordinates"]:
            obj.encoding["coordinates"] += " elat"
        if "elon" not in obj.encoding["coordinates"]:
            obj.encoding["coordinates"] += " elon"
    except Exception:
        obj.encoding["coordinates"] = "elon elat"


def check_grid_information(file):
    """
    Check if grid information is available in file.

    Parameters
    ----------
    file : str or xr.Dataset
        ICON data path or ICON data as xarray Dataset

    Returns
    ----------
    boolean

    See Also
    ----------
    iconarray.backend

    """
    if isinstance(file, pathlib.PurePath) or isinstance(file, str):
        data = open_dataset(file)
    else:
        data = file
    return "clon_bnds" in data.keys()


def combine_grid_information(file, grid_file):
    """
    Combine grid information.

    Parameters
    ----------
    file : file or ds
        data file
    grid_file : grid file or ds
        grid file

    Returns
    ----------
    ds : xarray.Dataset
        dataset

    Raises
    ----------
    TypeError
        Grid or data file cannot be opened to xr.core.dataset.Dataset
    WrongGridException
        Cell dimension and grid dimension are none

    See Also
    ----------
    iconarray.backend

    """
    if isinstance(grid_file, pathlib.PurePath) or isinstance(grid_file, str):
        try:
            grid = psy.open_dataset(grid_file)
        except ValueError:
            logging.error(f"The grid file {grid_file} was not found.")
            sys.exit()
    if isinstance(file, pathlib.PurePath) or isinstance(file, str):
        ds = open_dataset(file)
    else:
        ds = file

    try:
        ds = ds.squeeze()
    except AttributeError:
        logging.error("Model data contains more than one hypercube.")
        sys.exit()

    datasetType = xr.core.dataset.Dataset
    if type(ds) != datasetType or type(grid) != datasetType:
        raise TypeError(
            """Grid or data file could not be opened to xr.core.dataset.Dataset."""
        )

    cell_dim = get_cell_dim_name(ds, grid)
    if "cell" not in ds.dims and cell_dim is not None:
        ds = ds.rename_dims({cell_dim: "cell"})

    edge_dim = get_edge_dim_name(ds, grid)
    if "edge" not in ds.dims and edge_dim is not None:
        ds = ds.rename_dims({edge_dim: "edge"})

    if cell_dim is None and edge_dim is None:
        raise WrongGridException(grid)

    time_coord = get_time_coord_name(ds)
    if time_coord != "time":
        ds = ds.rename(
            {"time": ds.coords["time"].attrs["standard_name"], time_coord: "time"}
        ).expand_dims("time")
    if hasattr(ds, "time"):
        ds.time.attrs["axis"] = "T"

    if "cell" in ds.dims:
        ds = add_cell_data(ds, grid)
    if "edge" in ds.dims:
        ds = add_edge_data(ds, grid)

    for _k, v in six.iteritems(ds.data_vars):
        if "cell" in ds.data_vars[v.name].dims:
            _add_cell_encoding(v)
        if "edge" in ds.data_vars[v.name].dims:
            _add_edge_encoding(v)

    return ds


def get_cell_dim_name(ds, grid):
    """
    Get name of dimension in ICON data xarray dataset which identifies the cell dimension.

    Compares the length of the cell dimension in the grid dataset and compares with the ICON ouptut dataset, looking for a match.
    This assumes the dimension name for cells in the grid data is 'cell'.

    Parameters
    ----------
    ds : xarray.Dataset
        xarray.Dataset of ICON data.
    grid : xarray.Dataset
        xarray.Dataset of grid data.

    Returns
    ----------
    coord : str
        Name of the cell dimension. Defaults to None if not found.

    See Also
    ----------
    iconarray.backend

    """
    cell_dim = None
    dims = [key for key in ds.dims]
    for dim in dims:
        dim_value = ds.dims[dim]
        if (
            dim_value == grid.dims["cell"]
        ):  # maybe this needs to be dynamic, if grid has ncells as cell dim name
            cell_dim = dim
    return cell_dim


def get_edge_dim_name(ds, grid):
    """
    Get name of dimension in ICON data xarray dataset which identifies the edge dimension.

    Compares the length of the edge dimension in the grid dataset and compares with the ICON ouptut dataset, looking for a match.
    This assumes the dimension name for edge in the grid data is 'edge'.

    Parameters
    ----------
    ds : xarray.Dataset
        xarray.Dataset of ICON data.
    grid : xarray.Dataset
        xarray.Dataset of grid data.

    Returns
    ----------
    coord : str
        Name of the edge dimension. Defaults to None if not found.

    See Also
    ----------
    iconarray.backend

    """
    edge_dim = None
    dims = [key for key in ds.dims]
    for dim in dims:
        dim_value = ds.dims[dim]
        if (
            dim_value == grid.dims["edge"]
        ):  # maybe this needs to be dynamic, for example if grid has ncells as cell dim name, or edges vs edge
            edge_dim = dim
    return edge_dim


def get_time_coord_name(ds):
    """
    Get name of time coordinate in xarray dataset which has attribute standard_name = 'time' and datatype of datetime.

    Parameters
    ----------
    ds : xarray.Dataset
        xarray.Dataset of ICON data.

    Returns
    ----------
    coord : str
        Time coordinate. Defaults to 'time'.

    See Also
    ----------
    iconarray.backend

    """
    try:
        if ds.coords["time"].attrs["standard_name"] != "time":
            coords = [key for key in ds.coords]
            for coord in coords:
                if "datetime" in str(ds.coords[coord].dtype):
                    if "standard_name" in ds.coords[coord].attrs:
                        if ds.coords[coord].attrs["standard_name"] == "time":
                            return coord
        else:
            return "time"
    except Exception:
        return "time"


def add_cell_data(ds, grid):
    """
    Add clon, clat, clon_bnds, and clat_bnds coordinates from the grid file to the dataset.

    These coordinates are required when plotting cell variables.

    Parameters
    ----------
    ds : xarray.Dataset
        xarray.Dataset of ICON data.
    grid : xarray.Dataset
        xarray.Dataset of grid data.

    Returns
    ----------
    merged_ds : xarray.Dataset

    See Also
    ----------
    iconarray.backend

    """
    ds = (
        ds.assign_coords(clon=("cell", np.float32(grid.coords["clon"].values)))
        .assign_coords(clat=("cell", np.float32(grid.coords["clat"].values)))
        .assign_coords(
            clat_bnds=(
                ("cell", "vertices"),
                np.float32(grid.coords["clat_vertices"].values),
            )
        )
        .assign_coords(
            clon_bnds=(
                ("cell", "vertices"),
                np.float32(grid.coords["clon_vertices"].values),
            )
        )
    )

    ds.clon.attrs["standard_name"] = "longitude"
    ds.clon.attrs["long_name"] = "cell longitude"
    ds.clon.attrs["units"] = "radian"
    ds.clon.attrs["bounds"] = "clon_bnds"
    ds.clat.attrs["standard_name"] = "latitude"
    ds.clat.attrs["long_name"] = "cell latitude"
    ds.clat.attrs["units"] = "radian"
    ds.clat.attrs["bounds"] = "clat_bnds"
    return ds


def add_edge_data(ds, grid):
    """
    Add elon, elat, elon_bnds, and elat_bnds and other edge related coordinates from the grid file to the dataset.

    These elon, elat, elon_bnds, and elat_bnds coordinates are required when plotting edge variables. The following coordinates are also added which assist the plotting of edge vector variables:
    - zonal_normal_primal_edge: zonal component of the normal vector at the triangle edge midpoints
    - meridional_normal_primal_edge: meridional component of the normal vector at the triangle edge midpoints
    - edge_system_orientation
    - normal_edge
    - zn: normalized zonal_normal_primal_edge
    - mn: normalized meridional_normal_primal_edge

    Parameters
    ----------
    ds : xarray.Dataset
        xarray.Dataset of ICON data.
    grid : xarray.Dataset
        xarray.Dataset of grid data.

    Returns
    ----------
    merged_ds : xarray.Dataset

    See Also
    ----------
    iconarray.backend

    """
    ds = (
        ds.assign_coords(elon=("edge", np.float32(grid.coords["elon"].values)))
        .assign_coords(elat=("edge", np.float32(grid.coords["elat"].values)))
        .assign_coords(
            elat_bnds=(("edge", "no"), np.float32(grid.coords["elat_vertices"].values))
        )
        .assign_coords(
            elon_bnds=(("edge", "no"), np.float32(grid.coords["elon_vertices"].values))
        )
        .assign_coords(zonal_normal_primal_edge=grid["zonal_normal_primal_edge"])
        .assign_coords(
            meridional_normal_primal_edge=grid["meridional_normal_primal_edge"]
        )
        .assign_coords(edge_system_orientation=grid["edge_system_orientation"])
    )

    ds.elon.attrs["standard_name"] = "longitude"
    ds.elon.attrs["long_name"] = "edge longitude"
    ds.elon.attrs["units"] = "radian"
    ds.elon.attrs["bounds"] = "elon_bnds"
    ds.elat.attrs["standard_name"] = "latitude"
    ds.elat.attrs["long_name"] = "edge latitude"
    ds.elat.attrs["units"] = "radian"
    ds.elat.attrs["bounds"] = "elat_bnds"

    clat_ind_access = lambda x: grid.coords["clat"][x - 1]
    clon_ind_access = lambda x: grid.coords["clon"][x - 1]

    ds.coords["elat_bnds"][:, 2] = ds.coords["elat_bnds"][:, 1]
    ds.coords["elat_bnds"][:, 1] = xr.apply_ufunc(
        clat_ind_access, grid["adjacent_cell_of_edge"][1, :]
    )
    ds.coords["elat_bnds"][:, 3] = xr.apply_ufunc(
        clat_ind_access, grid["adjacent_cell_of_edge"][0, :]
    )
    ds.coords["elon_bnds"][:, 2] = ds.coords["elon_bnds"][:, 1]
    ds.coords["elon_bnds"][:, 1] = xr.apply_ufunc(
        clon_ind_access, grid["adjacent_cell_of_edge"][1, :]
    )
    ds.coords["elon_bnds"][:, 3] = xr.apply_ufunc(
        clon_ind_access, grid["adjacent_cell_of_edge"][0, :]
    )

    normal_edge = xr.concat(
        [ds.zonal_normal_primal_edge, ds.meridional_normal_primal_edge], dim="cart"
    )
    normal_edge = normal_edge / np.linalg.norm(normal_edge, axis=0)
    ds = ds.assign_coords(
        zn=ds.zonal_normal_primal_edge
        / np.sqrt(
            ds.zonal_normal_primal_edge**2 + ds.meridional_normal_primal_edge**2
        )
    )
    ds = ds.assign_coords(
        mn=ds.meridional_normal_primal_edge
        / np.sqrt(
            ds.zonal_normal_primal_edge**2 + ds.meridional_normal_primal_edge**2
        )
    )
    ds = ds.assign_coords(normal_edge=normal_edge)

    return ds


def open_dataset(file):
    """
    Open either NETCDF or GRIB file.

    Returning either an xarray.Dataset, or a list of xarray.Datasets if the
    data in the GRIB file cannot be represented as a single hypercube (see
    https://github.com/ecmwf/cfgrib for more info)

    Parameters
    ----------
    file : Path
        Path to ICON data file, either NETCDF of GRIB format.

    Returns
    ----------
    ds : xarray.Dataset or List(xarray.Datasets)

    Raises
    ----------
    TypeError
        If datatype is neither identified as GRIB or NETCDF.

    See Also
    ----------
    iconarray.backend

    """
    datatype = _identify_datatype(file)
    if datatype == "nc":
        return _open_NC(file)
    elif datatype == "grib":
        dss = _open_GRIB(file)
        if len(dss) == 1:
            return dss[0]
        else:
            return dss
    else:
        raise TypeError("Data is neither GRIB nor NETCDF.")


def _identify_datatype(file):
    if _identifyNC(file):
        return "nc"
    elif _identifyGRIB(file):
        return "grib"
    else:
        return False


def _identifyNC(file):
    # Identifies if NETCDF data and return True or False.
    msg = False
    with codecs.open(file, "r", encoding="utf-8", errors="ignore") as fdata:
        fd = fdata.read(3)
    if fd in ["CDF", "HDF"]:
        msg = True
    return msg


def _identifyGRIB(file):
    # Identifies if GRIB data and return True or False.
    with codecs.open(file, "r", encoding="utf-8", errors="ignore") as file:
        file_type = file.read(4)
        if file_type.lower() == "grib":
            return True
        else:
            return False


def _open_NC(file):
    return psy.open_dataset(file)


def _open_GRIB(file):
    #  Returns an array of xarray.Datasets.
    dss = cfgrib.open_datasets(
        file,
        backend_kwargs={
            "indexpath": "",
            "errors": "ignore",
        },
        encode_cf=("time", "geography", "vertical"),
    )
    return dss


def check_vertex2cell(ds_grid: xr.Dataset):
    """Check consistency of the vertex->cell connectivity.

    It requires an identical comparison of
    the tables of vertex->cell and vertex->edge->cell after removing duplicates

    Parameters
    ----------
    ds_grid: xr.Dataset
        dataset of the grid, which contains coordinates and neighbour lookup tables

    Returns
    -------
    True if consistency check is successful

    Raises
    ------
    ValueError
        if negative indices (expect for special value -1) are found in the neighbor lookup tables
    """
    if np.count_nonzero(ds_grid["edge_of_cell"] == -1):
        raise ValueError("negative neighbour indices of edge_of_cell not expected")

    nvertex = ds_grid.dims["vertex"]
    mask = np.transpose(ds_grid["edges_of_vertex"].data).flatten()

    # two dimensional array that will contain for each out of bound neighbor (-1) of the edge cell,
    # the pair (-1, -1) and NaN for the rest. Later on, one of the two -1 will be removed
    # by the algorithm that removes repetitions
    preghost = np.where(mask == -1, mask, np.NaN)

    ghost_data = np.reshape(np.concatenate((preghost, preghost)), (2, nvertex * 6))

    vertex2cell = ds_grid["adjacent_cell_of_edge"][
        :, np.transpose(ds_grid["edges_of_vertex"].data).flatten() - 1
    ].data

    def aunique(arr):
        res = np.unique(arr)
        # The unique is to remove repetitions, but not various -1. If so we recover them
        return np.append(res, np.repeat(-1, 6 - len(res)))

    # 6 x ncells (1D) array that contains all the cells of an iteration cell->edge->vertex
    vertex2cell = np.where(mask == -1, ghost_data, vertex2cell)
    vertex2cell = np.reshape(np.transpose(vertex2cell).flatten(), (nvertex, 12))
    vertex2cell = np.apply_along_axis(aunique, -1, vertex2cell)

    if vertex2cell.shape != (nvertex, 6):
        return False

    vertex2cell = np.transpose(vertex2cell)

    return np.array_equal(
        np.apply_along_axis(np.sort, 0, vertex2cell),
        np.apply_along_axis(np.sort, 0, ds_grid["cells_of_vertex"].data),
    )


def check_cell2vertex(ds_grid: xr.Dataset):
    """Check consistency of the cell->vertex connectivity.

    It requires an identical comparison of
    the tables of cell->vertex and cell->edge->vertex after removing duplicates

    Parameters
    ----------
    ds_grid: xr.Dataset
        dataset of the grid, which contains coordinates and neighbour lookup tables

    Returns
    -------
    True if consistency check is successful

    Raises
    ------
    ValueError
        if negative indices (expect for special value -1) are found in the neighbor lookup tables
    """
    if np.count_nonzero(ds_grid["edge_of_cell"] == -1):
        raise ValueError("negative neighbour indices of edge_of_cell not expected")

    ncells = ds_grid.dims["cell"]
    mask = np.transpose(ds_grid["edge_of_cell"].data).flatten()

    # two dimensional array that will contain for each out of bound neighbor (-1) of the edge cell,
    # the pair (-1, -1) and NaN for the rest. Later on, one of the two -1 will be removed
    # by the algorithm that removes repetitions
    preghost = np.where(mask == -1, mask, np.NaN)
    ghost_data = np.reshape(np.concatenate((preghost, preghost)), (2, ncells * 3))

    cell2vertex = ds_grid["edge_vertices"][
        :, np.transpose(ds_grid["edge_of_cell"].data).flatten() - 1
    ].data

    # 6 x ncells (1D) array that contains all the cells of an iteration cell->edge->vertex
    cell2vertex = np.where(mask == -1, ghost_data, cell2vertex)
    cell2vertex = np.reshape(np.transpose(cell2vertex).flatten(), (ncells, 6))

    def aunique(arr):
        res = np.unique(arr)
        # The unique is to remove repetitions, but not various -1. If so we recover them
        return np.append(res, np.repeat(-1, 3 - len(res)))

    cell2vertex = np.apply_along_axis(aunique, -1, cell2vertex)

    if cell2vertex.shape != (ncells, 3):
        return False

    cell2vertex = np.transpose(cell2vertex)

    return np.array_equal(
        np.apply_along_axis(np.sort, 0, cell2vertex),
        np.apply_along_axis(np.sort, 0, ds_grid["vertex_of_cell"].data),
    )


def check_cell2cell(ds_grid: xr.Dataset):
    """Check consistency of the cell->cell connectivity.

    It requires an identical comparison of
    the tables of cell->cell and cell->edge->cell after removing duplicates

    Parameters
    ----------
    ds_grid: xr.Dataset
        dataset of the grid, which contains coordinates and neighbour lookup tables

    Returns
    -------
    True if consistency check is successful
    """
    ncells = ds_grid.dims["cell"]
    mask = np.transpose(ds_grid["edge_of_cell"].data).flatten()

    # two dimensional array that will contain for each out of bound neighbor (-1) of the edge cell,
    # the pair (-1, cell_index) and NaN for the rest. We will use this pair to replace the
    # (cell of edge) for the -1 edge. Out of the pair (-1, cell_index) the cell_index will be later
    # eliminated (since it is the repetition of the original cell center) by the del_ind mask and only -1
    # will remain
    ghost_data = np.reshape(
        np.concatenate(
            (
                np.where(mask == -1, mask, np.NaN),
                np.where(mask == -1, np.repeat(np.arange(1, ncells + 1), 3), np.NaN),
            )
        ),
        (2, ncells * 3),
    )

    cell2cell = ds_grid["adjacent_cell_of_edge"][
        :, np.transpose(ds_grid["edge_of_cell"].data).flatten() - 1
    ].data

    # 6 x ncells (1D) array that contains all the cells of an iteration cell->edge->cell
    cell2cell = np.transpose(np.where(mask == -1, ghost_data, cell2cell)).flatten()

    # The tranverse cell->edge->cell contains 3 times the origin cell center. We remove it.
    del_ind = np.repeat(np.arange(1, ncells + 1), 6)
    del_ind = cell2cell != del_ind

    if len(cell2cell[del_ind]) != ncells * 3:
        return False

    cell2cell = np.transpose(np.reshape(cell2cell[del_ind], (ncells, 3))).flatten()
    return np.array_equal(cell2cell.data, ds_grid["neighbor_cell_index"].data.flatten())


def grid_consistency_check(ds_grid: xr.Dataset):
    """Perform consistency check of the grid.

    It checks various (not all) neighbor lookup tables

    Parameters
    ----------
    ds_grid: xr.Dataset
        dataset of the grid, which contains coordinates and neighbour lookup tables

    Returns
    -------
    True if consistency check is successful
    """
    ncells = ds_grid.dims["cell"]
    inds = np.repeat(np.arange(1, ncells + 1), 3)

    # neighbor cell index table can not contain its own cell center index
    if (inds == np.transpose(ds_grid["neighbor_cell_index"].data).flatten()).any():
        return False

    nvertex = ds_grid.dims["vertex"]
    inds = np.repeat(np.arange(1, nvertex + 1), 6)

    # neighbor vertex index table can not contain its own vertex index
    if (inds == np.transpose(ds_grid["vertices_of_vertex"].data).flatten()).any():
        return False

    return (
        check_cell2cell(ds_grid)
        & check_cell2vertex(ds_grid)
        & check_vertex2cell(ds_grid)
    )
