# Gaze Duration Error

Gazerr is an application for estimating the expected error in a gaze duration
measurement derived from repeated application of a point of gaze model.
It is particularly applicable to machine learning models that work with device
cameras to predict a stream of gaze fixation points from facial images.

The method requires an input dataset of validation points from the point
of gaze predictive model. This data is used to generate the probability 
distribution of true gaze durations given a measured gaze duration.

### Installation

Install from source code or from PyPi

### Usage

The application can be used from the command line by passing in a path to the
calibration file and the parameters for the duration measurement that will be
bounded. Note: that the penultimate two parameters should be comma separated sets
of integers that depict x,y coordiantes in pixels. The measurement length and
session lenth should be expressed in milliseconds.

The final parameter is a path to a directory in which to store the raw results

```
gazerr <CALIBRATION> <MEASUREMENT> <SESSION> <TARGET TOP LEFT> <TARGET BOTTOM RIGHT> <RESULTS>
```

To use the application without installing it you can employ the runner script.
Example below, using the supplied calibration data:

```
mkdir results/MREC_MAE_50
python ./gazerr-runner.py data/validation_50_MAE.csv 400 1000 40,40 340,290 results/MREC_MAE_50
```

Alternatively, you may inspect the code and use the library functions directly
inside your own application.

## Experiments

All experiments for the research paper can be executed via a series of scripts.

Create synthetic calibration data by running
```
python scripts/generate_datasets.py
```

Then execute the gazerr exeriments with the following two commands:
```
scripts/RUN_EXPERIMENTS.sh
scripts/RUN_BIAS_EXPERIMENTS.sh
```

Finally, analyse the results and generate the plots with
```
scripts/ANALYSE_RESULTS.sh
```

### Documentation

Additional documentation to be made available on 
[Read the Docs](https://gazerr.readthedocs.io/en/latest/)

If you use `gazerr` in your research please cite the following article

```
@article{hawkins2022,
   author = {John Hawkins},
   year = {2022},
   title = {Estimating Gaze Duration Error from Eye Tracking Data},
   journal = {TBC}
}
```




