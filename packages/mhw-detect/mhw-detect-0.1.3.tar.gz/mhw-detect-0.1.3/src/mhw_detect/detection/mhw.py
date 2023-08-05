import os
import multiprocessing as mp
from functools import partial
import pandas as pd
import yaml
import click
from typing import Tuple

from src.mhw_detect.detection.parser import parse_data, parse_param, count_files
from src.mhw_detect.detection.detect import prepare_data


@click.command(
    help="""
    Detect extreme events
    """
)
@click.option(
    "--config", "-c", type=str, required=True, help="Specify configuration file"
)
@click.option(
    "--geographical-subset",
    "-g",
    type=(
        click.FloatRange(min=-90, max=90),
        click.FloatRange(min=-90, max=90),
        click.FloatRange(min=-180, max=180),
        click.FloatRange(min=-180, max=180),
    ),
    help="The geographical subset as "
    + "minimal latitude, maximal latitude, "
    + "minimal longitude and maximal longitude",
)
def extreme_events(config: str, geographical_subset: Tuple[float, float, float, float]):
    conf = yaml.safe_load(open(config, "r"))

    output = conf["output_detection"]
    param = parse_param(conf)

    if geographical_subset != None:
        data = parse_data(conf, False)

        lat = geographical_subset[0:2]
        lon = geographical_subset[2:4]

        prepare_data(
            0, output, lat=lat, lon=lon, p=param["pctile"], deptht=0, **data, **param
        )

        print("Creating csv")
        df = pd.read_csv(os.path.join(output, "0.txt"), sep=";")
        df.to_csv(os.path.join(output, "data.csv"), sep=";")

    else:
        data = parse_data(conf)
        nfile = count_files(conf)

        pool = mp.Pool()
        pool.map(
            partial(prepare_data, outdir=output, p=param["pctile"], **data, **param),
            range(1, nfile),
        )
        pool.close()
        pool.join()

        print("Computation done")

        print("Creating csv")

        def f(i):
            return pd.read_csv(i, sep=";")

        filepaths = [output + str(i) + ".txt" for i in range(1, nfile)]
        df = pd.concat(map(f, filepaths))
        df.to_csv(os.path.join(output, "data.csv"), sep=";")


if __name__ == "__main__":
    extreme_events()
