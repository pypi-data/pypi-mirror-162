
# DALiuGE example components

[![codecov](https://codecov.io/gh/ICRAR/daliuge-component-examples/branch/main/graph/badge.svg?token=daliuge-component-examples_token_here)](https://codecov.io/gh/ICRAR/daliuge-component-examples)
[![CI](https://github.com/ICRAR/daliuge-component-examples/actions/workflows/main.yml/badge.svg)](https://github.com/ICRAR/daliuge-component-examples/actions/workflows/main.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository contains dlg_example_cmpts created by ICRAR. These are mostly meant to demonstrate how to implement some of the more advanced [DALiuGE](https://github.com/ICRAR/daliuge) features in a component. Please refer to the main [DALiuGE documentation](https://daliuge.readthedocs.io) for more information.

## Installation

There are multiple options for the installation, depending on how you are intending to run the DALiuGE engine, directly in a virtual environment (host) or inside a docker container. You can also install it either from PyPI (latest released version).

## Install it from PyPI

### Engine in virtual environment
```bash
pip install dlg_example_cmpts
```
### Engine in Docker container
```bash
docker exec -t daliuge-engine bash -c 'pip install --prefix=$DLG_ROOT/code dlg_example_cmpts'
```
NOTE: If you had this package installed already you will need to re-start the engine after that.
## Usage
For example the MyBranch component will be available to the engine when you specify 
```
dlg_example_cmpts.apps.MyBranch
```
in the AppClass field of a Python Branch component. The EAGLE palette associated with these components are also generated and can be loaded directly into EAGLE. In that case all the fields are correctly populated for the respective components.
