import os
import datetime
import xarray as xr
import numpy as np

import src.mhw_detect.detection.marineHeatWavesOpt as mhw


def subset(ds, lat, lon):
    if "latitude" in ds.coords:
        return ds.sel(latitude=slice(lat[0], lat[1]), longitude=slice(lon[0], lon[1]))
    else:
        return ds.sel(lat=slice(lat[0], lat[1]), lon=slice(lon[0], lon[1]))


def prepare_data(
    iter,
    outdir,
    lat=None,
    lon=None,
    deptht=0,
    p=90,
    data=None,
    clim=None,
    percent=None,
    **kwargs
):
    txtfile = os.path.join(outdir, str(iter) + ".txt")
    if (lat is not None) and (lon is not None):
        ds = subset(xr.open_dataset(data[0]), lat, lon)
    else:
        print("Opening file:", data[0] + str(iter) + ".nc")
        ds = xr.open_dataset(data[0] + str(iter) + ".nc")

    if "depth" in ds.coords:
        ds = ds.isel(depth=deptht)

    ds = ds[data[1]]

    if (clim is not None) or (percent is not None):
        if (lat is not None) and (lon is not None):
            climato = subset(xr.open_dataset(clim[0]), lat, lon)
            percentile = subset(xr.open_dataset(percent[0]), lat, lon)
        else:
            climato = xr.open_dataset(clim[0] + str(iter) + ".nc")
            percentile = xr.open_dataset(percent[0] + str(iter) + ".nc")

        climato = climato[clim[1]]

        percentile = percentile.sel(quantile=str(p / 100))
        percentile = percentile[percent[1]]
    else:
        climato = None
        percentile = None

    compute_detection(ds, txtfile, climato, percentile, **kwargs)


def compute_detection(ds, txtfile, climato=None, percent=None, **kwargs):

    if "latitude" in ds.coords:
        var_lat = "latitude"
        var_lon = "longitude"
    else:
        var_lat = "lat"
        var_lon = "lon"

    lat = len(ds[var_lat])
    lon = len(ds[var_lon])

    # Data preloading for fast cache retrieval
    data = ds.values
    if (climato is not None) and (percent is not None):
        thresh_climYear = percent.values
        seas_climYear = climato.values

    t_mhw = np.array(
        [
            datetime.datetime.utcfromtimestamp(t.astype("O") / 1e9).toordinal()
            for t in ds.time.values
        ]
    )

    with open(txtfile, "w") as f:
        f.write("lat;lon;time_deb;duration;categ;imax;imean\n")

        for latitude in range(0, lat):
            for longitude in range(0, lon):

                temp = data[:, latitude, longitude]

                if len(np.where(np.isnan(temp))[0]) < (80 / 100) * len(temp):

                    temp[temp < 0] = np.nan

                    if (climato is None) or (percent is None):
                        mhw_prop, mhw_date = mhw.detect(t_mhw, temp, **kwargs)
                    else:
                        mhw_prop, mhw_date = mhw.detect(
                            t_mhw,
                            temp,
                            thresh_climYear=thresh_climYear[:, latitude, longitude],
                            seas_climYear=seas_climYear[:, latitude, longitude],
                            **kwargs
                        )

                    if len(mhw_prop["time_start"]) != 0:
                        for num_mhw in range(len(mhw_prop["time_start"])):
                            lat_str = str(ds[var_lat][latitude].values)
                            lon_str = str(ds[var_lon][longitude].values)
                            time = str(mhw_date["date_start"][num_mhw])
                            duree = str(int(mhw_prop["duration"][num_mhw]))
                            categorie = str(mhw_prop["category"][num_mhw])
                            imax = str(mhw_prop["intensity_max"][num_mhw])
                            imean = str(mhw_prop["intensity_mean"][num_mhw])

                            f.write(
                                lat_str
                                + ";"
                                + lon_str
                                + ";"
                                + time
                                + ";"
                                + duree
                                + ";"
                                + categorie
                                + ";"
                                + imax
                                + ";"
                                + imean
                                + "\n"
                            )
