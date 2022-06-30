"""tests for crop module."""
import os
import xarray as xr
import iconarray


def test_crop():
    """Test of cropping functions.

    The tests do not check for exact results that the crop operation is correct but rather
    approximation that the resulting grid is within certain bounds.
    The consistenty check of the grid will ensure that various equivalent traversals of the topology of the grid
    produce same results, for example c->c == c->e->c
    The bounds for the check of the edges is a bit relaxed with respect to the selection area, since
    the crop algorithm do consider full cell triangles and certain edges can fall out of the region
    """
    basedir = os.path.dirname(os.path.realpath(__file__))
    in_cell_data = (
        basedir + "/data/lfff00010000_lon:0.152-0.154_lat:0.8745-0.8755_cell.nc"
    )
    in_edge_data = (
        basedir + "/data/lfff00010000_lon:0.152-0.154_lat:0.8745-0.8755_edge.nc"
    )
    in_grid = (
        basedir + "data/icon_grid_0001_R19B08_lon:0.152-0.154_lat:0.8745-0.8755.nc"
    )

    ds_grid = xr.open_dataset(in_grid)
    ds_cell = xr.open_dataset(in_cell_data)
    ds_edge = xr.open_dataset(in_edge_data)

    lon_bnds = [0.1525, 0.1535]
    lat_bnds = [0.8748, 0.8752]
    crop = iconarray.Crop(ds_grid, lon_bnds, lat_bnds)
    assert iconarray.grid_consistency_check(crop.rgrid)

    cell_cropped = crop(ds_cell)
    edge_cropped = crop(ds_edge)

    min_lon = cell_cropped["clon"].min().data
    max_lon = cell_cropped["clon"].max().data
    min_lat = cell_cropped["clat"].min().data
    max_lat = cell_cropped["clat"].max().data

    assert (
        (min_lon > lon_bnds[0])
        & (max_lon < lon_bnds[1])
        & (min_lat > lat_bnds[0])
        & (max_lat < lat_bnds[1])
    )

    elon_bnds = [0.15245, 0.1536]
    elat_bnds = [0.87475, 0.8753]

    min_lon = edge_cropped["elon"].min().data
    max_lon = edge_cropped["elon"].max().data
    min_lat = edge_cropped["elat"].min().data
    max_lat = edge_cropped["elat"].max().data

    assert (
        (min_lon > elon_bnds[0])
        & (max_lon < elon_bnds[1])
        & (min_lat > elat_bnds[0])
        & (max_lat < elat_bnds[1])
    )


if __name__ == "__main__":
    test_crop()
