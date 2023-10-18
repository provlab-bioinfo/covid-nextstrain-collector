# covid-nextstrain-collector
 [![Lifecycle: WIP](https://img.shields.io/badge/lifecycle-WIP-yellow.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/CompEpigen/scMethrix/issues) [![License: GPL3](https://img.shields.io/badge/license-GPL3-lightgrey.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html) [![minimal Python version: 3.10](https://img.shields.io/badge/Python-3.10-6666ff.svg)](https://www.r-project.org/) [![Package Version = 0.0.1](https://img.shields.io/badge/Package%20version-0.0.1-orange.svg?style=flat-square)](https://github.com/provlab-bioinfo/covid-nextstrain-collector/blob/main/NEWS) [![Last-changedate](https://img.shields.io/badge/last%20change-2023--10--18-yellowgreen.svg)](https://github.com/provlab-bioinfo/covid-nextstrain-collector/blob/main/NEWS)

<!-- [![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FCompEpigen%2FscMethrix&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com) -->
<!--[![R-CMD-check](https://github.com/CompEpigen/scMethrix/workflows/R-CMD-check/badge.svg)](https://github.com/CompEpigen/scMethrix/actions) -->

## Introduction

Collector for sequencing information and accompanying metadata for SARS-CoV-2 samples at APL for visualization in Nextstrain<sup>[1](#references)</sup>. This retrieves the necessary sequencing data and metadata files for generating the Nextstrain instance.

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

See [```REQUIREMENTS.txt```](REQUIREMENTS.txt) for package dependancies.

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

## Input

A config template is provided in the repo. The config file should look like this:
```json
{
    "seqDataPath": "/path/to/BNexport",
    "patientDataDir": "/path/to/metadata",
    "routineSeqDB": "/path/to/database"
}
```

These three paths are necessary for collection:

- **Sequencing data** (```seqDataPath```): The folder containing the exports from the BioNumerics database. 
- **Patient metadata** (```patientDataDir```): The folder containing the aggregated patient metadata from all COVID samples. 
- **Routine seq database:** (```routineSeqDB```) A text file containing a list of all files from which to search for FASTA files corresponding to each sample.

## Output

Two files are generated and can be placed into the Auspice ```/data/``` folder for generating the Nextstrain instance:
- **sequences.fasta:** A multi-FASTA file containing all FASTA sequences for the inputted samples. The FASTA headers match the ```strain``` column in ```metadata.tsv```.
- **metadata.tsv:** The collated data for the SARS-CoV-2 analysis and patient metadata. This contains the minimum columns necessary for Nextstrain generation: ```strain``` and ```date``` (```YYYY-MM-DD```).

## References

1. Hadfield, James, et al. "Nextstrain: real-time tracking of pathogen evolution." Bioinformatics 34.23 (2018): 4121-4123.