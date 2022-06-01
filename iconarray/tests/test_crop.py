import xarray as xr
from iconarray.core.crop import Crop
import cfgrib
from iconarray.backend.grid import combine_grid_information


def test_crop():

    in_data = "/code/rz+/icon_data_processing_incubator/data/ICON/R19B08/lfff00010000"
    in_grid = "/code/rz+/icon_data_processing_incubator/data/ICON/R19B08/icon_grid_0001_R19B08_mch.nc"

    ds_grid = xr.open_dataset(in_grid)
    dss = cfgrib.open_datasets(
        in_data,
        backend_kwargs={
            "errors": "ignore",
            "read_keys": ["typeOfLevel", "gridType"],
            "filter_by_keys": {"typeOfLevel": "generalVerticalLayer"},
        },
        encode_cf=("time", "geography", "vertical"),
    )
    ds_cell = combine_grid_information(dss[0], in_grid)

    crop = Crop(ds_grid, [0.165, 0.18], [0.8, 0.81])
    grid_cropped = crop.crop_grid()
    data_cropped = crop.crop_data(ds_cell)


if __name__ == "__main__":
    test_crop()
