# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['detection']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'dask>=2021.10.0',
 'netCDF4>=1.5.7',
 'numba>=0.54.1',
 'numpy>=1.20.3',
 'pandas>=1.3.5',
 'scipy>=1.7.3',
 'xarray>=2022.6.0,<2023.0.0']

entry_points = \
{'console_scripts': ['mhw-detect = '
                     'src.mhw_detect.detection.mhw:extreme_events']}

setup_kwargs = {
    'name': 'mhw-detect',
    'version': '0.1.3',
    'description': 'Fast marine heatwaves and extrem events detector based on https://github.com/ecjoliver/marineHeatWaves',
    'long_description': "# MHW Detector\n\nMarine heatwaves detector based on https://github.com/ecjoliver/marineHeatWaves.  \n\nThis package integrates a numba optimised version of ecjoliver's implementation for MHW detection with multiprocessing capabilities to compute detection over every coordinates of the dataset.  \n\nThis code is not only for detecting MHW. It can also be used to detect extrem events of any variables like chla, pH, O2, etc...\n\n## Installation\n> pip install mhw-detect\n\n\n## Usage\n### Diagramme\n![architecture](mhw_archi.png)\n\n### Command\n#### Detection\n> mhw-detect -c config.yml  \n\n#### Geospatial cut\n> mhw-cut -c config.yml\n",
    'author': 'John Brouillet',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
