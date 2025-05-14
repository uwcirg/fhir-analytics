# FHIR Analytics
Analytics experiments on FHIR data

## Setup
### Requirements
This repo requires python3 to run the Jupyter notebook server, and Java to use the pathling python module

The Jupyter notebook server may require firewall overrides, especially when access from across the internet

### Get Code
Clone this repo to desired location

    git clone https://github.com/uwcirg/fhir-analytics

### Install
#### Jupyter Notebook
Install the Jupyter notebook server, `jupyterlab` as follows:

    python3 -m pip install --user jupyterlab

#### Notebook Dependencies
Each notebook may have its own dependencies, but at the moment all require `pathling` to analyze FHIR data. Install `pathling` as follows

    python3 -m pip install --user pathling

### Run
To start the Jupyter notebook server, run

    jupyter lab

If you're sharing a notebook over the internet, invoke `jupyter` as follows

    jupyter lab --ip 0.0.0.0

Select the desired notebook (`.ipynb` file) in the file browser, or via File => Open from Path

## Live Demo
mybinder.org can automatically provision environments for Jupyter notebook server from GitHub URLs.

To open a notebook from this repo on mybinder.org, follow the below link:

https://mybinder.org/v2/gh/uwcirg/fhir-analytics/HEAD?urlpath=/doc/tree/pathling-poc.ipynb
