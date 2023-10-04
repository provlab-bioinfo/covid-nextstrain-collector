# covid-nextstrain-collector
[![Lifecycle:
experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)

## Introduction

Collector for sequencing data and accompanying metadata for SARS-CoV-2 samples at APL for visualization in Nextstrain.

## Table of Contents

- [Introduction](#introduction)
- [Quick-Start Guide](#quick-start%guide)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Input](#input)
- [Output](#output)
- [Workflow](#workflow)
- [References](#references)

## Quick-Start Guide

Import into your script:
```
conda activate hnoss-env
import hnoss
```
For details on available arguments, enter:
```
hnoss --help
```

## Dependencies

[Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) is required to build an environment with required workflow dependencies. To create the environment
```
conda create -n hnoss-env
```
then add the following channels
```
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
```
and then install hnoss
```
conda install hnoss
```

See REQUIREMENTS.txt for package dependancies.

## Config

A config template is provided in the repo. The config file should look like this:
```json
{
    "seqDataPath": "/path/to/BNexport",
    "patientDataDir": "/path/to/metadata",
    "routineSeqDB": "/path/to/database"
}
```

## Input
Three paths are necessary for collection:

- **Sequencing data:** The folder containing the exports from the BioNumerics database. These are generated during each sequencing run, and should be stored in ```/APL_Genomics/virus_covid19/routineSeq/run/BNexport/```.
- **Patient metadata:** The folder containing the aggregated patient metadata from all COVID samples. These should be stored in ```/Groups/ProvincialSurveillance/COVID-19/```
- **Routine seq database:** A text file containing a list of all files present in ```/routineSeq/```. This is used for finding the corresponding FASTA files for each sample.

## Output
Two files are generated and can be placed into the Nextstrain ```/data/``` folder for generating the Nextstrain instance:
- **sequences.fasta:** A multi-fasta file containing all fasta sequences for the inputted samples. The fasta headers match the ```strain``` column in ```metadata.tsv```.
- **metadata.tsv:** The collated data for the SARS-CoV-2 analysis and patient metadata. This contains the minimum columns necessary for Nextstrain generation (```strain```, ```date``` in YYYY-MM-DD).

## References

1. Karthikeyan, Smruthi, et al. "Wastewater sequencing uncovers early, cryptic SARS-CoV-2 variant transmission (preprint)." (2021).

2. Andersen-Lab Andersen-Lab/Freyja: Depth-weighted De-Mixing https://github.com/andersen-lab/Freyja (accessed Oct 4, 2023). 