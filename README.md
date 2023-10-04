# covid-nextstrain-collector
[![Lifecycle:
experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)

## Introduction

Collector for sequencing information and accompanying metadata for SARS-CoV-2 samples at APL for visualization in Nextstrain<sup>[1](#references)</sup>.

## Table of Contents

- [Introduction](#introduction)
- [Quick-Start Guide](#quick-start-guide)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Config](#config)
- [Input](#input)
- [Output](#output)
- [References](#references)

## Quick-Start Guide

To run the script:
```bash
conda activate covid-nextstrain-collector
covid-nextstrain-collector.py --config /path/to/config --output /path/to/output
```

## Dependencies

See [REQUIREMENTS.txt](REQUIREMENTS.txt) for package dependancies.

## Installation

[Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) is required to build an environment with required workflow dependencies:

```bash
conda create -n covid-nextstrain-collector python=3.10 --file REQUIREMENTS.txt
conda activate covid-nextstrain-collector
```

From the top-level of this repo, use pip to install the app module:

```bash
pip install .
```

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

1. Hadfield, James, et al. "Nextstrain: real-time tracking of pathogen evolution." Bioinformatics 34.23 (2018): 4121-4123.

2. Andersen-Lab Andersen-Lab/Freyja: Depth-weighted De-Mixing https://github.com/andersen-lab/Freyja (accessed Oct 4, 2023). 