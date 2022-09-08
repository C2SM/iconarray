"""
The utilities.py module contains various functions useful for analysing or plotting (ICON) data using xarray.

Contains public functions: ind_from_latlon, add_coordinates, get_stats wilks, show_data_vars
"""

import numpy as np
import six
import xarray
from scipy import stats


def awhere_drop(ds, cond):
    """
    xarray.Dataset.where equivalent that preserves the dtype of the array.

    The xarray.Dataset.where in general will not preserve the value type of the array. In case of drop=False, elements of the array that do not satisfy the condition are set to np.NaN, which can only be stored on a float type. Therefore the return of xarray.Dataset.where will be of dtype float64. This function computes a where with drop=True, ensuring the dtype of the input xarray is preserved.

    Parameters
    ----------
    ds : xr.Dataset
        Dataset such as ICON data
    cond
        A condition to apply to the data.

    Returns
    ----------
    reduced_ds : xr.Dataset
        Filtered dataset
    """
    ret = ds.where(cond, drop=True)
    for var in ds:
        ret[var] = ret[var].astype(ds[var].dtype)

    return ret


def ind_from_latlon(lats, lons, lat, lon, verbose=False):
    """
    Find the nearest neighbouring index to given location.

    Parameters
    ----------
    lats : 2d array
        Latitude grid
    lons : 2d array
        Longitude grid
    lat : float
        Latitude of location
    lon : float
        Longitude of location
    verbose : bool
        Print information. Defaults to False.

    Returns
    ----------
    index : int
        Index of nearest grid point.

    See Also
    ----------
    iconarray.core.utilities

    Examples
    ----------
    >>> # Get values of grid cell closest to coordinate
    >>> # E.g. Zürich:
    >>> lon = 8.54
    >>> lat = 47.38
    >>> lats = np.rad2deg(ds.clat.values[:])
    >>> lons = np.rad2deg(ds.clon.values[:])
    >>> ind = iconarray.ind_from_latlon(
    ...         lats,lons,lat,lon,verbose=True
    ...         )

    >>> ind
    3352
    # Closest ind: 3352
    #  Given lat: 47.380 vs found lat: 47.372
    #  Given lon: 8.540 vs found lon: 8.527

    """
    dist = [
        np.sqrt((lats[i] - lat) ** 2 + (lons[i] - lon) ** 2) for i in range(len(lats))
    ]
    ind = np.where(dist == np.min(dist))[0][0]
    if verbose:
        print(f"Closest ind: {ind}")
        print(f" Given lat: {lat:.3f} vs found lat: {lats[ind]:.3f}")
        print(f" Given lon: {lon:.3f} vs found lon: {lons[ind]:.3f}")
    return ind


def add_coordinates(lon, lat, lonmin, lonmax, latmin, latmax):
    """
    Get the position of given lat/lon coordinates in relation to the bounds of regular lat/lon grid.

    This could be used for example to add a marker to a map plot by lat/lon coordinates.

    Parameters
    ----------
    lon : float
        Longitude of location
    lat : float
        Latitude of location
    lonmin : float
        Minimum longitude of map extent
    lonmax: float
        Maximum longitude of map extent
    latmin : float
        Minimum latitude of map extent
    latmax: float
        Maximum latitude of map extent

    Returns
    ----------
    pos_lon: float
        Position of given longitude on map plot
    pos_lat: float
        Position of given latitude on map plot

    See Also
    ----------
    iconarray.core.utilities

    Examples
    ----------
    >>> # Add marker at certain location on map
    >>> # E.g. Zürich:
    >>> lon = 8.54
    >>> lat = 47.38
    >>> lonmin = 5.8
    >>> lonmax = 10.7
    >>> latmin = 45.5
    >>> latmax = 48.0
    >>> pp = ds.psy.plot.mapplot(name="temp", map_extent[lonmin,lonmax,latmin,latmax])
    >>> pos_lon, pos_lat = iconarray.add_coordinates(lon, lat, lonmin, lonmax, latmin, latmax)
    >>> fig.axes[0].plot(pos_lon, pos_lat, transform=fix.axes[0].transAxes)
    """
    llon = lonmax - lonmin
    llat = latmax - latmin
    pos_lon = (lon - lonmin) / llon
    pos_lat = (lat - latmin) / llat
    return pos_lon, pos_lat


def get_stats(varin1, varin2):
    """
    Get mean, difference of mean and p value for the T-test of the means of two independent samples (varin1, varin2).

    Parameters
    ----------
    varin1 : float
        First sample
    varin2 : float
        Second sample (must have the same shape as varin1, except in axis=0)

    Returns
    ----------
    varin1_mean: array
        Mean of first sample
    varin2_mean: array
        Mean of second sample
    varin_diff: float
        Difference of means
    pval: float
        p-value for the T-test of the means

    See Also
    ----------
    iconarray.core.utilities

    Examples
    ----------
    >>> # Get means, difference and p values comparing two model outputs (ds1 and ds2)
    >>> var1_mean, var2_mean, var_diff, var_pval = iconvis.get_stats(ds1['T'].values, ds2['T'].values)
    >>> # Get data points, which are significantly different at level 0.05
    >>> pval_sig = np.argwhere(var_pval>0.05)
    """
    varin1_mean = np.mean(varin1, axis=0)
    varin2_mean = np.mean(varin2, axis=0)
    varin_diff = varin2_mean - varin1_mean
    # compute p values
    pval = stats.ttest_ind(varin1, varin2, 0)[1]
    return varin1_mean, varin2_mean, varin_diff, pval


def wilks(pvals, alpha):
    """
    Get threshold for p-values at which differences are significant at level alpha if the dependency of data points is accounted for according to Wilks et al. 2016 (https://doi.org/10.1175/BAMS-D-15-00267.1).

    Parameters
    ----------
    pvals : array
        p-values
    alpha : float
        Significance level

    Returns
    ----------
    pfdr: float
        Threshold for significance

    See Also
    ----------
    iconarray.core.utilities

    Examples
    ----------
    >>> # Get data points, which are significantly different at level 0.05 when accounting for data dependency
    >>> _,_,_,var_pval = iconvis.get_stats(ds1['T'].values, ds2['T'].values)
    >>> pfdr = iconvis.wilks(var_pval, 0.05)
    >>> pval_sig = np.argwhere(var_pval>pfdr)
    """
    pval_1d = pvals.ravel()
    pval_rank = np.sort(pval_1d)
    N = np.size(pvals)
    alpha_fdr = 2 * alpha
    for i in range(len(pval_rank)):
        j = i + 1
        if pval_rank[i] > (j / N) * alpha_fdr:
            break
    pfdr = pval_rank[i]
    return pfdr


# show_data_vars can be used in python scripts to find out which variable name psyplot will need to plot that variable.
# eg if GRIB_cfVarName is defined, cfgrib will set this as the variable name, as opposed to GRIB_shortName.
def show_data_vars(ds):
    """
    Print a table with variables in dataset.

    The first column is the variable name chosen by cfgrib to use eg. when plotting with psyplot.

    Parameters
    ----------
    ds : xarray.Dataset
        Dataset of ICON GRIB data opened with cgrib engine or cfgrib.
    """
    if type(ds) is str:
        Exception(
            "Argument is not a Dataset. Please open the dataset via psy.open_dataset() and pass returned Dataset to this function."
        )
    elif type(ds) is xarray.core.dataset.Dataset:
        print(
            "{:<15} {:<32} {:<20} {:<20} {:<10}".format(
                "psyplot name", "long_name", "GRIB_cfVarName", "GRIB_shortName", "units"
            )
        )
        for _k, v in six.iteritems(ds.data_vars):
            i = ds.data_vars[v.name]
            try:
                long_name = (
                    (i.long_name[:28] + "..") if len(i.long_name) > 28 else i.long_name
                )
            except Exception:
                long_name = ""
            try:
                units = i.units
            except Exception:
                units = ""
            try:
                gribcfvarName = i.GRIB_cfVarName
            except Exception:
                gribcfvarName = ""
            try:
                gribshortName = i.GRIB_shortName
            except Exception:
                gribshortName = ""
            print(
                "{:<15} {:<32} {:<20} {:<20} {:<10}".format(
                    v.name, long_name, gribcfvarName, gribshortName, units
                )
            )
