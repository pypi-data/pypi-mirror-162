# MHW Detector

Marine heatwaves detector based on https://github.com/ecjoliver/marineHeatWaves.  

This package integrates a numba optimised version of ecjoliver's implementation for MHW detection with multiprocessing capabilities to compute detection over every coordinates of the dataset.

## Installation
> pip install mhw-detect


## Usage
### Diagramme
![architecture](mhw_archi.png)

### Command
#### Detection
> mhw-detect -c config.yml  

#### Geospatial cut
> mhw-cut -c config.yml
