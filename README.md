# flo-sync

Tools for aligning and comparing physiological signals from two devices: FP data and LabChart data.

## What This Project Does

This repository contains a small analysis workflow for comparing cardiac output (CO) from LabChart against velocity time integral (VTI) from FP data. The workflow:

1. Loads the two source files from the data directory.
2. Corrects the FP timeline across stages.
3. Estimates stage-specific time offsets using cross-correlation on heart rate.
4. Resamples the LabChart signal to the FP time base.
5. Produces summary statistics and comparison plots in the notebook.

The main walkthrough is in [notebooks/technical.ipynb](notebooks/technical.ipynb).

## Data

The input data is not publicly available. See [data/README.md](data/README.md) for the expected file naming convention and placement rules.

## Environment

The project uses Pixi for environment management. The core dependencies are defined in [pixi.toml](pixi.toml).

## Repository Layout

- [src/loaders.py](src/loaders.py): file loading helpers for FP and LabChart data.
- [src/processors.py](src/processors.py): time correction, resampling, and stage offset estimation.
- [src/plotters.py](src/plotters.py): plotting helpers for HR traces and comparison plots.
- [notebooks/technical.ipynb](notebooks/technical.ipynb): end-to-end analysis notebook.

## AI Usage

See [AI_USAGE.md](AI_USAGE.md) for a short description of how AI was used while preparing this assignment.