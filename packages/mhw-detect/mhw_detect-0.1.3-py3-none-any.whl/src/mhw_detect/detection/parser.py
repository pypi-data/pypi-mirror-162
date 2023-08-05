import os
import glob

def check_precalc_clim_thresh(data):
    if not {"clim", "percent"} <= data.keys():
        print(
            "Precalculated mean and/or percentile have not been referenced in config file. \
        They will be recalculated by Hobday's method"
        )


def parse_data(conf, cut=True):
    if cut:
        parse_path = lambda p: os.path.join(os.path.dirname(p), "Cut_")
    else:
        parse_path = lambda p: p

    data = {
        datas: [parse_path(conf["data"][datas]["path"]), conf["data"][datas]["var"]]
        for datas in conf["data"]
    }
    check_precalc_clim_thresh(data)
    return data


def parse_param(conf):
    return {params: conf["params"][params] for params in conf["params"]}


def count_files(conf):
    return (
        len(
            [
                name
                for name in glob.glob(
                    os.path.dirname(conf["data"]["data"]["path"]) + "/Cut_*.nc"
                )
            ]
        )
        + 1
    )
